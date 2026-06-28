# -*- coding: utf-8 -*-
"""AI 教研助手 Function Calling 工具定义 + 执行器"""
from __future__ import annotations

from typing import TYPE_CHECKING
from backend.Agent.memory import MemoryStore  # noqa: F401 — 向后兼容

if TYPE_CHECKING:
    from backend.Agent.personality import Personality


# ============================================================
# 工具定义（OpenAI function calling 格式）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "record_memory",
            "description": "记录用户说过的重要信息（研究方向、偏好、日程、经历）",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["research", "preference", "schedule", "experience"],
                                 "description": "research研究方向 preference偏好 schedule日程 experience经历"},
                    "content": {"type": "string", "description": "要记录的具体内容，一句话总结"},
                },
                "required": ["category", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_memory",
            "description": "查询关于用户的长期记忆，搜索相关往事",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_state",
            "description": "获取当前 AI 助手状态（语气、投入度、关注度、静默时长）",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期时间和星期几。需要感知时间上下文时必须调用",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_silence_hours",
            "description": "查看距离用户最后一次发消息过了多久。长时间沉默时调用",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_tone",
            "description": "根据对话氛围调整语气",
            "parameters": {
                "type": "object",
                "properties": {
                    "tone": {"type": "string", "enum": ["professional", "casual", "encouraging", "analytical"],
                             "description": "目标语气"},
                },
                "required": ["tone"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_engagement",
            "description": "根据对话质量调整投入度。深度教学研讨+5，敷衍回应-3",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta": {"type": "integer", "description": "投入度变化值"},
                },
                "required": ["delta"],
            },
        },
    },
]


# ============================================================
# 工具执行器（build_tool_map 模式 — 从 XiaoBai 迁移）
# ============================================================

def build_tool_map(personality: "Personality", memory_store: MemoryStore):
    """构建工具名 → 执行函数的映射，替代 if/elif 链"""
    return {
        "record_memory": lambda **kw: memory_store.add(kw["content"], kw["category"]),
        "check_memory": lambda **kw: memory_store.search(kw["keyword"]),
        "get_state": lambda **kw: personality.get_status(),
        "get_current_time": lambda **kw: personality.get_current_time(),
        "get_silence_hours": lambda **kw: personality.get_silence_hours(),
        "set_tone": lambda **kw: personality.set_tone(kw["tone"]),
        "adjust_engagement": lambda **kw: personality.adjust_engagement(int(kw["delta"])),
    }
