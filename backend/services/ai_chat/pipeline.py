# -*- coding: utf-8 -*-
"""三阶段管道 + 辅助函数

chat() 骨架:
  tool_map   = _make_tool_map()         # 代码层工具映射，整个管道复用
  extraction = phase1_extract()         # AI: 提取意图/关键词/实体
  context    = collect_context()        # 代码: 所有工具 + 记忆 + 统计
  optimized  = phase1_optimize()        # AI: 整合上下文 → 摘要
  prompt     = phase2_assemble()        # 代码: 五层 system prompt
  reply      = phase3_respond()         # AI: function calling 循环
"""
from __future__ import annotations

import json
from typing import Tuple, Dict

from backend.Agent.provider import get_ai_provider
from backend.Agent.personality import Personality
from backend.Agent.memory import MemoryStore
from backend.Agent.tools import TOOLS, build_tool_map
from backend.Agent.rules import (
    MAX_CONTEXT_MESSAGES, MAX_TOOL_ROUNDS,
    SUMMARIZE_THRESHOLD, KEEP_LAST, DEFAULT_MODEL,
)
from backend.Agent.achievements import AchievementStore, ACHIEVEMENTS
from backend.Agent.preprocessor import Preprocessor, PreprocessResult
from backend.Agent.prompt_builder import build_layered_prompt, build_achievement_rules
from backend.Agent.tool_router import split_tool_definitions
from backend.core.config import settings
from backend.schema.vo.ai_chat import AchievementVO
from .helpers import build_history_summary


# ═══════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════

def enforce_silence(personality: Personality):
    """沉默 > 2h: 投入度 -2/h, 关注度 → 发散态"""
    h = personality.silence_timing / 3600
    if h > 2:
        personality.engagement = max(0, personality.engagement - int(h * 2))
        personality.attention = min(30, personality.attention)


def summarize_and_trim(history: list, memory: MemoryStore, model: str) -> list:
    """上下文过长时 AI 总结旧消息 → 写入记忆 → 保留最近 KEEP_LAST 条"""
    if len(history) <= SUMMARIZE_THRESHOLD:
        return history
    to_summarize = history[:-KEEP_LAST] if len(history) > KEEP_LAST else history
    if len(to_summarize) < 10:
        return history[-KEEP_LAST:]
    lines = []
    for m in to_summarize:
        role = m.get("role", "")
        content = m.get("content", "") or ""
        if role in ("user", "assistant") and content:
            tag = "教师" if role == "user" else "AI助手"
            lines.append(f"{tag}: {content}")
    if not lines:
        return history[-KEEP_LAST:]
    try:
        provider = get_ai_provider(model)
        resp = provider.chat([{"role": "user",
            "content": f"把以下对话总结为一段话（100字以内，不要换行）：\n" + "\n".join(lines)}])
        summary = resp.get("content", "").strip()
        if summary:
            memory.add(f"[对话摘要] {summary}", "experience")
    except Exception:
        pass
    return history[-KEEP_LAST:]


def resolve_model(pre: PreprocessResult, engagement: int = 0,
                  user_model: str = None, enable_deep_think: bool = True) -> str:
    """模型路由: 用户指定 > 投入度 >= 90 → pro > AI 判深度 → pro > flash"""
    if user_model:
        return user_model
    if enable_deep_think and (engagement >= 90 or pre.deep_think_needed):
        return "deepseek-v4-pro"
    return DEFAULT_MODEL


def _make_tool_map(personality: Personality, memory: MemoryStore) -> dict:
    """构建代码层工具映射，整个管道复用一次。不含成就回调（Phase 3 另建）。"""
    return build_tool_map(personality, memory, unlock_ach_cb=None)


# ═══════════════════════════════════════════════════════
# 管道函数
# ═══════════════════════════════════════════════════════

def phase1_extract(message: str, history: list, tool_map: dict) -> dict:
    """AI 提取 — 轻量模型分析用户消息，返回结构化 JSON。

    返回: intent / keywords / entities / search_needed / deep_think_needed
    """
    pre_provider = get_ai_provider(settings.PREPROCESS_MODEL)
    preprocessor = Preprocessor(
        provider=pre_provider,
        tool_executor=lambda name, **kw: tool_map[name](**kw),
    )
    return preprocessor._extract(message, build_history_summary(history))


def collect_context(extraction: dict, message: str, raw_message: str,
                    personality: Personality, memory: MemoryStore,
                    ach_store: AchievementStore, tool_map: dict) -> dict:
    """代码收集 — 所有工具调用 + 记忆检索 + 统计，集中在一处。

    入参:
      tool_map — 由 _make_tool_map() 构建，整个管道复用
    返回:
      tool_results      — 所有代码层工具结果
      retrieval_results — 个人记忆检索结果
    """
    tool_results: Dict[str, str] = {}
    entities = extraction.get("entities", {})
    safety_input = raw_message or message

    # ── 通用工具: calc / translate / safety（关键词匹配）──
    from backend.Agent.preprocessor import should_call_calc, should_call_translate, should_set_safety_tone

    if should_call_calc(message, entities):
        expr = entities.get("expression", "")
        try:
            tool_results["calc"] = tool_map["calc"](expression=expr) if expr else "需要从用户输入提取表达式"
        except Exception:
            pass

    if should_call_translate(message, entities):
        text = entities.get("text", message)
        target = entities.get("target", "zh")
        try:
            tool_results["translate"] = tool_map["translate"](text=text, target=target)
        except Exception:
            pass

    if should_set_safety_tone(safety_input):
        try:
            tool_results["set_tone"] = tool_map["set_tone"](tone="safety")
        except Exception:
            pass

    # ── 个人状态: get_state / get_current_time / get_silence_timing ──
    for name in ("get_state", "get_current_time", "get_silence_timing"):
        try:
            tool_results[name] = tool_map[name]()
        except Exception:
            pass

    # ── 个人记忆检索: Phase 1 关键词 → MemoryStore 三层检索 ──
    personal = []
    seen = set()
    for kw in extraction.get("keywords", []):
        if not kw or kw in seen:
            continue
        seen.add(kw)
        for r in memory.query(kw, personality.engagement):
            c = r.get("content", "")
            if c not in seen:
                seen.add(c)
                personal.append(r)
    personal.sort(key=lambda m: m.get("recall_score", 0), reverse=True)
    retrieval_results = personal[:8]

    # ── 统计 → 成就追踪 ──
    stat_map = {
        "calc": "tool_calc", "translate": "tool_translate",
        "set_tone": "tone_safety_triggered",
        "get_current_time": "tool_get_current_time",
        "get_silence_timing": "tool_get_silence_hours",
    }
    for name in tool_results:
        if name in stat_map:
            ach_store.increment_stat(stat_map[name])
        ach_store.append_stat("tools_used", name)

    return {"tool_results": tool_results, "retrieval_results": retrieval_results}


def phase1_optimize(message: str, extraction: dict, context: dict,
                    tool_map: dict) -> str:
    """AI 优化 — 整合原始输入 + 提取信息 + 工具结果 → 紧凑摘要。"""
    pre_provider = get_ai_provider(settings.PREPROCESS_MODEL)
    preprocessor = Preprocessor(
        provider=pre_provider,
        tool_executor=lambda name, **kw: tool_map[name](**kw),
    )
    return preprocessor._optimize(message, extraction, context["tool_results"])


def phase2_assemble(optimized: str, extraction: dict, context: dict,
                    personality: Personality, user_state: dict,
                    user_name: str) -> str:
    """代码组装 — 五层 system prompt 纯格式化，不调任何外部服务。

    Layer 1: 系统指令  Layer 2: 状态  Layer 3: 记忆
    Layer 4: 预处理    Layer 5: 用户状态
    """
    pre = PreprocessResult(
        intent=extraction.get("intent", ""),
        keywords=extraction.get("keywords", []),
        entities=extraction.get("entities", {}),
        tool_results=context["tool_results"],
        retrieval_results=context["retrieval_results"],
        optimized_context=optimized,
        search_needed=extraction.get("search_needed", False),
        deep_think_needed=extraction.get("deep_think_needed", False),
    )
    ach_rules = build_achievement_rules(set(user_state.get("unlocked_ach_ids", [])))
    prompt = build_layered_prompt(pre, personality, user_name, user_state)
    return prompt + "\n\n" + ach_rules


def phase3_respond(system_prompt: str, history: list, personality: Personality,
                   memory: MemoryStore, ach_store: AchievementStore, model: str
                   ) -> Tuple[str, list]:
    """AI 主模型 — function calling 循环 (max 3 轮)。

    工具: check_memory / record_memory / adjust_engagement
          / adjust_attention / unlock_achievement / set_tone
    """
    _, main_tools = split_tool_definitions(TOOLS)
    provider = get_ai_provider(model)

    messages = [{"role": "system", "content": system_prompt}]
    messages += history[-MAX_CONTEXT_MESSAGES:]

    ai_achievements = []

    def _ach_callback(ach_id):
        for ach in ACHIEVEMENTS:
            if ach["id"] == ach_id:
                r = ach_store.force_unlock(ach)
                if r:
                    ai_achievements.append(AchievementVO(
                        id=r["id"], name=r["name"], desc=r["desc"],
                        emoji=r["emoji"], tier=r.get("tier", "bronze"),
                    ))
                return r["name"] if r else "已解锁"
        return "未知成就"

    # Phase 3 需要成就回调，另建一个 tool_map
    tool_map = build_tool_map(personality, memory, _ach_callback)
    tools_seen = set()
    ai_content = ""

    for _ in range(MAX_TOOL_ROUNDS):
        response = provider.chat(messages, main_tools, "auto")
        tool_calls = response.get("tool_calls", [])
        if not tool_calls:
            ai_content = response.get("content", "")
            break

        messages.append({"role": "assistant",
                         "content": response.get("content") or "",
                         "tool_calls": tool_calls})

        for tc in tool_calls:
            fn = tc["function"]
            args = json.loads(fn["arguments"])
            handler = tool_map.get(fn["name"])
            result = handler(**args) if handler else f"未知工具：{fn['name']}"
            tools_seen.add(fn["name"])
            if fn["name"] == "check_memory":
                ach_store.increment_stat("tool_check_memory")
            messages.append({"role": "tool", "tool_call_id": tc["id"],
                            "content": result})
    else:
        messages.append({"role": "user", "content": "请根据已有信息用自然语言回复用户。"})
        final = provider.chat(messages)
        ai_content = final.get("content", "抱歉，我暂时无法回答这个问题。")

    for t in tools_seen:
        ach_store.append_stat("tools_used", t)

    return ai_content, ai_achievements
