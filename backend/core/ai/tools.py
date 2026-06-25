# -*- coding: utf-8 -*-
"""AI 教研助手 Function Calling 工具定义 — 从 XiaoBai 迁移适配"""
import json
import os
import re
from datetime import datetime


# ============================================================
# 工具定义（OpenAI function calling 格式）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "记住用户的信息（偏好、习惯、研究方向、经历等），之后对话中自然引用",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "需要记住的事实，尽量完整"},
                    "category": {"type": "string", "enum": ["research", "preference", "schedule", "experience"],
                                 "description": "事实类别：research研究方向 preference个人偏好 schedule日程安排 experience经历"}
                },
                "required": ["fact", "category"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "查询之前记住的关于用户的信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "查询关键词，如'研究方向''公开课''语法教学'"},
                    "category": {"type": "string", "enum": ["research", "preference", "schedule", "experience"],
                                 "description": "可选，按类别筛选"}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_tone",
            "description": "根据对话氛围调整说话语气。自动判断是否需要切换",
            "parameters": {
                "type": "object",
                "properties": {
                    "tone": {"type": "string", "enum": ["professional", "casual", "encouraging", "analytical"],
                             "description": "professional专业严谨 casual轻松亲切 encouraging鼓励支持 analytical深入分析"}
                },
                "required": ["tone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "adjust_engagement",
            "description": "根据对话质量调整对用户投入度。深度教学研讨+5，敷衍回应-3",
            "parameters": {
                "type": "object",
                "properties": {
                    "delta": {"type": "integer", "description": "投入度变化值，正数升温负数降温"}
                },
                "required": ["delta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前日期时间，用于处理跟时间相关的请求",
            "parameters": {"type": "object", "properties": {}}
        }
    },
]


# ============================================================
# 记忆系统（JSON 文件存储）
# ============================================================

class MemoryStore:
    """用户长期记忆 — JSON 文件存储 + 关键词搜索"""

    def __init__(self, user_id: int, base_dir: str):
        self.user_id = user_id
        self.path = os.path.join(base_dir, f"user_{user_id}_memory.json")
        self._memories: list = self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._memories, f, ensure_ascii=False, indent=2)

    def add(self, fact: str, category: str) -> str:
        entry = {
            "fact": fact,
            "category": category,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        # 去重：同一个 fact 不存两次
        for m in self._memories:
            if m["fact"] == fact:
                return f"已存在相同记忆，不重复存储"
        self._memories.append(entry)
        self.save()
        return f"已记住：{fact}"

    def search(self, keyword: str, category: str = None) -> str:
        results = []
        for m in self._memories:
            if category and m["category"] != category:
                continue
            if keyword.lower() in m["fact"].lower():
                results.append(f"[{m['category']}] {m['fact']} ({m['time']})")
        if not results:
            return f"未找到关于'{keyword}'的记忆"
        return "\n".join(results[-5:])  # 最多返回 5 条

    def get_recent_context(self, n: int = 10) -> str:
        """获取最近 N 条记忆，注入 system prompt"""
        if not self._memories:
            return ""
        recent = self._memories[-n:]
        return "关于用户的记忆：\n" + "\n".join(
            f"- [{m['category']}] {m['fact']}" for m in recent
        )


# ============================================================
# 工具执行器
# ============================================================

def execute_tool(tool_name: str, arguments: dict, personality, memory_store: MemoryStore) -> str:
    """执行 function calling 工具，返回结果文本"""
    if tool_name == "remember":
        return memory_store.add(arguments["fact"], arguments["category"])
    elif tool_name == "recall":
        return memory_store.search(arguments["keyword"], arguments.get("category"))
    elif tool_name == "set_tone":
        return personality.set_tone(arguments["tone"])
    elif tool_name == "adjust_engagement":
        return personality.adjust_engagement(int(arguments["delta"]))
    elif tool_name == "get_time":
        now = datetime.now()
        return f"现在是 {now.strftime('%Y年%m月%d日')}，{['周一','周二','周三','周四','周五','周六','周日'][now.weekday()]} {now.strftime('%H:%M')}"
    return f"未知工具：{tool_name}"
