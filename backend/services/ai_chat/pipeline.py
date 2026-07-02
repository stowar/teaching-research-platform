# -*- coding: utf-8 -*-
"""三阶段管道 + 辅助函数"""
from __future__ import annotations

import json
from typing import Tuple

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


# ── 管道辅助（独立函数）───────────────────────────

def enforce_silence(personality: Personality):
    h = personality.silence_timing / 3600
    if h > 2:
        personality.engagement = max(0, personality.engagement - int(h * 2))
        personality.attention = min(30, personality.attention)


def summarize_and_trim(history: list, memory: MemoryStore, model: str) -> list:
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
        resp = provider.chat([{"role": "user", "content": f"把以下对话总结为一段话（100字以内，不要换行）：\n" + "\n".join(lines)}])
        summary = resp.get("content", "").strip()
        if summary:
            memory.add(f"[对话摘要] {summary}", "experience")
    except Exception:
        pass
    return history[-KEEP_LAST:]


def resolve_model(pre: PreprocessResult, engagement: int = 0,
                  user_model: str = None, enable_deep_think: bool = True) -> str:
    """根据投入度 + AI 判断决定用 flash 还是 pro。

    搜索不换模型，由 web_search 工具实现。
    优先级: 用户指定 > 阈值触发 pro > 默认 flash
    """
    if user_model:
        return user_model
    if enable_deep_think and (engagement >= 90 or pre.deep_think_needed):
        return "deepseek-v4-pro"
    return DEFAULT_MODEL


def make_tool_executor(personality: Personality, memory: MemoryStore):
    full_map = build_tool_map(personality, memory, unlock_ach_cb=None)

    def execute(tool_name: str, **kwargs) -> str:
        handler = full_map.get(tool_name)
        if handler is None:
            return f"未知工具: {tool_name}"
        try:
            return handler(**kwargs)
        except TypeError:
            if not kwargs:
                return f"工具 {tool_name} 需要参数"
            try:
                return handler()
            except Exception:
                return f"工具 {tool_name} 参数不足"

    return execute


# ── 三阶段管道 ───────────────────────────────────

def phase1_preprocess(message: str, history: list, personality: Personality,
                      memory: MemoryStore, ach_store: AchievementStore) -> PreprocessResult:
    """Phase 1: 通用预处理 — 轻量模型提取 + 通用工具（calc/translate）。"""
    pre_provider = get_ai_provider(settings.PREPROCESS_MODEL)
    preprocessor = Preprocessor(
        provider=pre_provider,
        tool_executor=make_tool_executor(personality, memory),
    )
    result = preprocessor.run(message, build_history_summary(history))

    stat_map = {"calc": "tool_calc", "translate": "tool_translate",
                 "set_tone": "tone_safety_triggered"}
    for name in result.tool_results:
        if name in stat_map:
            ach_store.increment_stat(stat_map[name])
        ach_store.append_stat("tools_used", name)

    return result


def phase2_personalize(pre: PreprocessResult, personality: Personality,
                       memory: MemoryStore, ach_store: AchievementStore,
                       user_state: dict, user_name: str) -> str:
    """Phase 2: 个性化层 — 个人状态工具 + 个人记忆检索 + 组装 prompt。"""
    tool_map = build_tool_map(personality, memory, unlock_ach_cb=None)

    # 个人状态工具 — 始终注入
    for name in ("get_state", "get_current_time", "get_silence_timing"):
        try:
            pre.tool_results[name] = tool_map[name]()
        except Exception:
            pass

    for name in ("get_current_time", "get_silence_timing"):
        if name in pre.tool_results:
            stat_map = {"get_current_time": "tool_get_current_time",
                         "get_silence_timing": "tool_get_silence_hours"}
            ach_store.increment_stat(stat_map[name])

    # 个人记忆检索
    personal = []
    seen = set()
    for kw in pre.keywords:
        if not kw or kw in seen:
            continue
        seen.add(kw)
        for r in memory.query(kw, personality.engagement):
            c = r.get("content", "")
            if c not in seen:
                seen.add(c)
                personal.append(r)
    personal.sort(key=lambda m: m.get("recall_score", 0), reverse=True)
    pre.retrieval_results = personal[:8]

    # 组装 prompt
    ach_rules = build_achievement_rules(set(user_state.get("unlocked_ach_ids", [])))
    prompt = build_layered_prompt(pre, personality, user_name, user_state)
    return prompt + "\n\n" + ach_rules


def phase3_generate(system_prompt: str, history: list, personality: Personality,
                    memory: MemoryStore, ach_store: AchievementStore, model: str
                    ) -> Tuple[str, list]:
    """Phase 3: 主模型生成 — function calling 循环（仅记忆和状态修改工具）。"""
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

    tool_map = build_tool_map(personality, memory, _ach_callback)
    tools_seen = set()
    ai_content = ""

    for _ in range(MAX_TOOL_ROUNDS):
        response = provider.chat(messages, main_tools, "auto")
        tool_calls = response.get("tool_calls", [])
        if not tool_calls:
            ai_content = response.get("content", "")
            break

        messages.append({"role": "assistant", "content": response.get("content") or "",
                         "tool_calls": tool_calls})

        for tc in tool_calls:
            fn = tc["function"]
            args = json.loads(fn["arguments"])
            handler = tool_map.get(fn["name"])
            result = handler(**args) if handler else f"未知工具：{fn['name']}"
            tools_seen.add(fn["name"])
            if fn["name"] == "check_memory":
                ach_store.increment_stat("tool_check_memory")
            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": result})
    else:
        messages.append({"role": "user", "content": "请根据已有信息用自然语言回复用户。"})
        final = provider.chat(messages)
        ai_content = final.get("content", "抱歉，我暂时无法回答这个问题。")

    for t in tools_seen:
        ach_store.append_stat("tools_used", t)

    return ai_content, ai_achievements
