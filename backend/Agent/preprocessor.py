# -*- coding: utf-8 -*-
"""预处理器（通用层）— 轻量模型提取 + 通用工具 + 上下文优化

面向所有人的通用层，不写入个人状态、不检索个人记忆。
个性化信息（state/memory）在 ai_chat.py 的 Phase 2 注入。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Callable

from backend.Agent.provider import IAIProvider
from backend.Agent.rules import CALC_KEYWORDS, TRANSLATE_KEYWORDS, SAFETY_KEYWORDS


# ── 关键词匹配函数（供代码和测试使用）─────────────

def should_call_calc(user_input: str, entities: dict = None) -> bool:
    text = user_input + json.dumps(entities or {}, ensure_ascii=False)
    return any(kw in text for kw in CALC_KEYWORDS)


def should_call_translate(user_input: str, entities: dict = None) -> bool:
    text = user_input + json.dumps(entities or {}, ensure_ascii=False)
    return any(kw in text for kw in TRANSLATE_KEYWORDS)


def should_set_safety_tone(user_input: str) -> bool:
    return any(kw in user_input for kw in SAFETY_KEYWORDS)


# ── PreprocessResult ──────────────────────────────

@dataclass
class PreprocessResult:
    """预处理阶段输出（通用层），供 prompt_builder 消费"""
    intent: str = ""
    keywords: List[str] = field(default_factory=list)
    entities: Dict[str, str] = field(default_factory=dict)
    tool_results: Dict[str, str] = field(default_factory=dict)      # 仅通用工具
    retrieval_results: list = field(default_factory=list)            # 由个性化层填充
    optimized_context: str = ""
    search_needed: bool = False      # 需要联网搜索
    deep_think_needed: bool = False  # 需要深度思考


# ── Preprocessor ──────────────────────────────────

class Preprocessor:
    """轻量模型两调用管道（通用层）。

    Call 1（AI）: 只提取意图/关键词/实体
    代码层: 关键词匹配 → 调通用工具（calc/translate）
    Call 2（AI）: 整合原始输入 + 提取信息 + 工具结果 → 优化摘要

    不接触 Personality / MemoryStore — 那些是个性化层的事。
    """

    def __init__(self, provider: IAIProvider, tool_executor: Callable[..., str]):
        self.provider = provider    # 服务提供商接口
        self._execute_tool = tool_executor

    def run(self, user_input: str, history_summary: str = "",
            safety_input: str = None) -> PreprocessResult:
        """执行通用层预处理。safety_input 用于安全检测（通常用原始输入）。"""
        # Call 1: 提取
        extraction = self._extract(user_input, history_summary)

        # 代码决定 + 执行通用工具（calc / translate / safety tone）
        tool_results: Dict[str, str] = {}
        entities = extraction.get("entities", {})

        if should_call_calc(user_input, entities):
            expr = entities.get("expression", "")
            try:
                tool_results["calc"] = (
                    self._execute_tool("calc", expression=expr)
                    if expr else "需要从用户输入提取表达式"
                )
            except Exception:
                pass

        if should_call_translate(user_input, entities):
            text = entities.get("text", user_input)
            target = entities.get("target", "zh")
            try:
                tool_results["translate"] = self._execute_tool("translate", text=text, target=target)
            except Exception:
                pass

        # 安全检测用原始输入，避免 OCR 文本误触发
        if should_set_safety_tone(safety_input or user_input):
            try:
                tool_results["set_tone"] = self._execute_tool("set_tone", tone="safety")
            except Exception:
                pass

        # Call 2: 优化上下文
        optimized = self._optimize(user_input, extraction, tool_results)

        return PreprocessResult(
            intent=extraction.get("intent", ""),
            keywords=extraction.get("keywords", []),
            entities=entities,
            tool_results=tool_results,
            optimized_context=optimized,
            search_needed=extraction.get("search_needed", False),
            deep_think_needed=extraction.get("deep_think_needed", False),
        )

    # ── Call 1: 提取 ──────────────────────────────

    def _extract(self, user_input: str, history_summary: str) -> dict:
        """轻量模型提取关键信息。只提取，不决定工具。"""
        system_prompt = """你是一个信息提取器。分析用户消息，返回JSON（直接返回JSON，不要markdown代码块，不要解释）。

输出格式：
{"intent": "意图", "keywords": ["关键词1"], "entities": {"类型": "值"}, "search_needed": false, "deep_think_needed": false}

intent: 教学咨询 / 计算请求 / 翻译请求 / 闲聊 / 其他
entities 可选键: expression(数学表达式) text(待翻译文本) target翻译目标 zh或en
search_needed: 涉及实时信息、新闻、政策、最新动态时为 true
deep_think_needed: 涉及复杂推理、多步分析、方案设计、对比论证时为 true

=== 示例 ===
用户: 帮我设计一节高职英语听说课的教案
{"intent":"教学咨询","keywords":["高职英语","听说课","教案设计"],"entities":{},"search_needed":false,"deep_think_needed":true}

用户: 2026年英语教学改革有什么新政策？
{"intent":"教学咨询","keywords":["英语教学改革","新政策","2026"],"entities":{},"search_needed":true,"deep_think_needed":false}

用户: 分析任务驱动法和传统讲授法的优缺点，给出建议
{"intent":"教学咨询","keywords":["任务驱动法","传统讲授法","对比分析"],"entities":{},"search_needed":false,"deep_think_needed":true}

用户: 计算 3.14 × 15² + 200
{"intent":"计算请求","keywords":["计算"],"entities":{"expression":"3.14*15**2+200"},"search_needed":false,"deep_think_needed":false}

用户: 帮忙算一下三角形的面积，底10高8
{"intent":"计算请求","keywords":["三角形","面积"],"entities":{"expression":"10*8/2"},"search_needed":false,"deep_think_needed":false}

用户: 把"课程设计"翻译成英文
{"intent":"翻译请求","keywords":["翻译"],"entities":{"text":"课程设计","target":"en"},"search_needed":false,"deep_think_needed":false}

用户: translate 高职英语教学改革 to English
{"intent":"翻译请求","keywords":["translate"],"entities":{"text":"高职英语教学改革","target":"en"},"search_needed":false,"deep_think_needed":false}

用户: 你好呀今天天气不错
{"intent":"闲聊","keywords":["问候","天气"],"entities":{},"search_needed":false,"deep_think_needed":false}

用户: 谢谢你的帮助
{"intent":"闲聊","keywords":["感谢"],"entities":{},"search_needed":false,"deep_think_needed":false}

用户: 用英语怎么说"教学评估"？
{"intent":"翻译请求","keywords":["翻译","教学评估"],"entities":{"text":"教学评估","target":"en"},"search_needed":false,"deep_think_needed":false}"""

        history_block = "\n---\n最近对话摘要：\n%s" % history_summary if history_summary else ""

        try:
            resp = self.provider.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "用户消息：%s%s" % (user_input, history_block)},
            ])
            content = (resp.get("content") or "{}").strip()
            m = re.search(r'```(?:json)?\s*\n?(.*?)```', content, re.DOTALL)
            if m:
                content = m.group(1).strip()
            return json.loads(content)
        except (json.JSONDecodeError, Exception):
            return {
                "intent": "其他",
                "keywords": [user_input[:30]] if user_input else [],
                "entities": {},
                "search_needed": False,
                "deep_think_needed": False,
            }

    # ── Call 2: 优化 ──────────────────────────────

    def _optimize(self, user_input: str, extraction: dict, tool_results: Dict[str, str],) -> str:
        """整合原始输入 + 提取信息 + 通用工具结果 → 紧凑摘要（动态长度）。"""
        tool_block = "\n".join(
            f"- {name}: {result}" for name, result in tool_results.items()
        ) if tool_results else "无"

        # 摘要长度按输入动态调整
        in_len = len(user_input)
        if in_len < 1000:
            max_chars = 200
        elif in_len < 3000:
            max_chars = 300
        elif in_len < 8000:
            max_chars = 400
        else:
            max_chars = 500

        prompt = f"""你是上下文优化器。基于以下信息，输出一段紧凑的上下文摘要（{max_chars}字以内），直接输出文本，不要JSON，不要解释。
    
                【原始用户输入】（必须保留原意）
                {user_input}
                
                【提取信息】
                意图: {extraction.get('intent', '未知')}
                关键词: {', '.join(extraction.get('keywords', []))}
                实体: {json.dumps(extraction.get('entities', {}), ensure_ascii=False)}
                
                【通用工具结果】
                {tool_block}
                
                请生成一段整合上下文，供主AI模型参考："""

        try:
            resp = self.provider.chat([{"role": "user", "content": prompt}])
            return (resp.get("content") or "").strip()
        except Exception:
            parts = [f"用户意图: {extraction.get('intent', '未知')}"]
            if tool_results:
                parts.append("工具: " + "; ".join(
                    f"{k}={v[:60]}" for k, v in tool_results.items()
                ))
            return " ".join(parts)
