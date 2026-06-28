# -*- coding: utf-8 -*-
"""用户长期记忆 — JSON 文件 + 内存缓存"""
import json
import os
from datetime import datetime


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

    def __len__(self):
        """支持 len(memory) 快速获取记忆数"""
        self._load()
        return len(self._cache)
