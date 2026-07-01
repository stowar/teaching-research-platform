# -*- coding: utf-8 -*-
"""AI 教研助手 Function Calling 工具定义 + 执行器"""
from __future__ import annotations

import json
import math

from backend.Agent.memory import MemoryStore
from backend.Agent.personality import Personality
from backend.Agent.achievements import ACHIEVEMENTS


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
            "name": "get_silence_timing",
            "description": "查看距离用户最后一次发消息过了多久（分钟/小时）。长时间沉默时调用",
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
    {
        "type": "function",
        "function": {
            "name": "adjust_attention",
            "description": "根据话题一致性调整关注度。话题深入/关联+5，话题跳转/分散-5",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta": {"type": "integer", "description": "关注度变化值"},
                },
                "required": ["delta"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unlock_achievement",
            "description": "当教师的对话内容命中课堂场景成就时调用，授予一个教学成就。仅在明确匹配成就描述时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "achievement_id": {
                        "type": "string",
                        "enum": [a["id"] for a in ACHIEVEMENTS if a.get("ai_judged")],
                        "description": "要解锁的成就 ID"
                    },
                },
                "required": ["achievement_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calc",
            "description": "执行数学计算。教师提及计算、统计、换算等需求时调用。支持加减乘除、幂运算、三角函数。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '3.14 * 15^2'"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "translate",
            "description": "翻译文本。教师需要中英互译或翻译教学材料时调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "待翻译文本"},
                    "target": {"type": "string", "enum": ["zh", "en"], "description": "目标语言：zh 中文，en 英文"},
                },
                "required": ["text", "target"],
            },
        },
    },
]


# ============================================================
# 工具执行器（build_tool_map 模式 — 从 XiaoBai 迁移）
# ============================================================

def _calc(expression: str) -> str:
    """安全 eval，仅允许数学运算"""
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed["__builtins__"] = {}
    allowed["abs"] = abs
    allowed["round"] = round
    allowed["min"] = min
    allowed["max"] = max
    allowed["pow"] = pow
    allowed["sum"] = sum
    # 别名 & Python 3.7 缺失的
    allowed["ln"] = math.log
    allowed["lg"] = math.log10

    def _comb(n, k): return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))
    def _perm(n, k): return math.factorial(n) // math.factorial(n - k)
    def _lcm(a, b): return a * b // math.gcd(a, b)
    allowed["comb"] = _comb
    allowed["perm"] = _perm
    allowed["lcm"] = _lcm

    try:
        result = eval(expression, {"__builtins__": {}}, allowed)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"


def _translate(text: str, target: str) -> str:
    """调用 AI 模型做翻译"""
    from backend.Agent.provider import get_ai_provider
    from backend.Agent.rules import DEFAULT_MODEL
    provider = get_ai_provider(DEFAULT_MODEL)
    lang = "中文" if target == "zh" else "English"
    prompt = f"将以下文本翻译为:{lang}，只输出译文，不要解释：\n{text}"
    try:
        resp = provider.chat([{"role": "user", "content": prompt}])
        return resp.get("content", "翻译失败").strip()
    except Exception as e:
        return f"翻译失败：{e}"


def build_tool_map(personality: Personality, memory_store: MemoryStore,
                   unlock_ach_cb=None):
    """构建工具名 → 执行函数的映射，替代 if/elif 链"""
    tm = {
        "record_memory": lambda **kw: memory_store.add(kw["content"], kw["category"]),
        "check_memory": lambda **kw: json.dumps(
            [{"content": m["content"], "tier": m.get("tier",""), "created": m.get("created_at","")}
             for m in memory_store.query(kw["keyword"], personality.engagement)],
            ensure_ascii=False
        ),
        "get_state": lambda **kw: personality.get_status(),
        "get_current_time": lambda **kw: personality.get_current_time(),
        "get_silence_timing": lambda **kw: personality.get_silence_timing(),
        "set_tone": lambda **kw: personality.set_tone(kw["tone"]),
        "adjust_engagement": lambda **kw: personality.adjust_engagement(int(kw["delta"])),
        "adjust_attention": lambda **kw: personality.adjust_attention(int(kw["delta"])),
        "calc": lambda **kw: _calc(kw["expression"]),
        "translate": lambda **kw: _translate(kw["text"], kw["target"]),
    }
    if unlock_ach_cb:
        tm["unlock_achievement"] = lambda **kw: unlock_ach_cb(kw["achievement_id"])
    return tm
