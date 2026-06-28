# -*- coding: utf-8 -*-
"""AI 教研助手 Function Calling 工具 + 记忆系统 — 从 XiaoBai 迁移适配"""
import json
import os
from datetime import datetime


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
# 记忆系统（JSON 文件 + 内存缓存）
# ============================================================

class MemoryStore:
    """用户长期记忆 — JSON 文件存储 + 内存缓存"""

    def __init__(self, user_id: int, base_dir: str):
        self.user_id = user_id
        self.path = os.path.join(base_dir, f"user_{user_id}_memory.json")
        self._cache: list = None
        self._load()

    def _load(self):
        if self._cache is not None:
            return self._cache
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache = data.get("memories", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self._cache = []
        return self._cache

    def _flush(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"memories": self._cache}, f, ensure_ascii=False, indent=2)

    def add(self, content: str, category: str) -> str:
        self._load()
        for m in self._cache:
            if m["content"] == content:
                return "已存在，不重复存储"
        self._cache.append({
            "category": category,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })
        self._flush()
        return f"已记住：{content}"

    def search(self, keyword: str) -> str:
        self._load()
        results = [m for m in self._cache if keyword.lower() in m["content"].lower()]
        if not results:
            return f"未找到关于'{keyword}'的记忆"
        return json.dumps(results[-5:], ensure_ascii=False)

    def format_for_prompt(self, n: int = 10) -> str:
        """格式化最近 N 条记忆注入 system prompt"""
        self._load()
        if not self._cache:
            return ""
        recent = self._cache[-n:]
        return "关于用户的重要记忆：\n" + "\n".join(
            f"- [{m['category']}] {m['content']}" for m in recent
        )


# ============================================================
# 工具执行器（build_tool_map 模式 — 从 XiaoBai 迁移）
# ============================================================

def build_tool_map(personality, memory_store: MemoryStore):
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
