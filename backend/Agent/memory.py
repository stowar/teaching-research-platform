# -*- coding: utf-8 -*-
"""用户长期记忆 — JSON 文件 + 内存缓存 + 三层检索"""
import json
import os
import re
from datetime import datetime, timedelta

# 记忆分级
TIER_CORE = "core"           # 核心：偏好、经历、研究方向
TIER_REFERENCE = "reference"  # 参考：日程、一般信息
TIER_PERIPHERAL = "peripheral"  # 边缘：摘要、一次性信息

TIER_SCORE = {TIER_CORE: 3, TIER_REFERENCE: 2, TIER_PERIPHERAL: 1}

# 类别 → 默认分级
CATEGORY_TIERS = {
    "preference": TIER_CORE,
    "experience": TIER_CORE,
    "research": TIER_CORE,
    "schedule": TIER_REFERENCE,
    "summary": TIER_PERIPHERAL,
}


class MemoryStore:
    """用户长期记忆 — JSON 文件存储 + 内存缓存 + 三层检索"""

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

    def _infer_tier(self, category: str, content: str) -> str:
        """根据类别 + 内容推断记忆分级"""
        return CATEGORY_TIERS.get(category, TIER_REFERENCE)

    def _age_days(self, m: dict) -> float:
        """计算记忆的天数"""
        created = m.get("created_at", "")
        try:
            dt = datetime.strptime(created, "%Y-%m-%d %H:%M")
            return (datetime.now() - dt).total_seconds() / 86400.0
        except ValueError:
            return 999.0

    def add(self, content: str, category: str) -> str:
        self._load()
        for m in self._cache:
            if m["content"] == content:
                return "已存在，不重复存储"
        tier = self._infer_tier(category, content)
        self._cache.append({
            "category": category,
            "content": content,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "tier": tier,
            "recall_count": 0,
            "protected": tier == TIER_CORE,
        })
        self._flush()
        return f"已记住：{content}"

    def is_protected(self, content: str) -> bool:
        """检查记忆是否为核心保护级别"""
        self._load()
        for m in self._cache:
            if m["content"] == content:
                return m.get("protected", False) or m.get("tier", "") == TIER_CORE
        return False

    def delete(self, content: str) -> str:
        """删除记忆——核心记忆受保护，不可删除"""
        self._load()
        for i, m in enumerate(self._cache):
            if m["content"] == content:
                if m.get("protected", False) or m.get("tier", "") == TIER_CORE:
                    return "核心记忆受保护，不可删除"
                self._cache.pop(i)
                self._flush()
                return f"已删除：{content}"
        return "未找到该记忆"

    # ── 三层检索算法 ────────────────────────────

    def query(self, keyword: str, engagement: int) -> list:
        """
        三层记忆检索：
          L1 — 投入度 → 搜索范围（低→核心 / 中→核心+参考 / 高→全量）
          L2 — 记忆分级 → 基础分数（core=3 / reference=2 / peripheral=1）
          L3 — 时间衰减 → 最终权重 = 基础分 × 衰减系数
        返回按最终权重排序的记忆列表
        """
        self._load()
        keyword_lower = keyword.lower()

        # ── L1: 投入度 → 查询模式 ──
        if engagement < 30:
            allowed_tiers = {TIER_CORE}
        elif engagement < 70:
            allowed_tiers = {TIER_CORE, TIER_REFERENCE}
        else:
            allowed_tiers = {TIER_CORE, TIER_REFERENCE, TIER_PERIPHERAL}

        # ── L2: 关键词匹配 + 分级基础分 ──
        scored = []
        for m in self._cache:
            tier = m.get("tier", TIER_REFERENCE)
            if tier not in allowed_tiers:
                continue

            content = m.get("content", "")
            # 精确匹配 > 部分匹配 > 无匹配
            if keyword_lower in content.lower():
                match_score = 2.0 if keyword_lower == content.lower() else 1.0
            else:
                match_score = 0.3  # 模糊匹配给低分

            base = TIER_SCORE.get(tier, 2) * match_score
            if base <= 0:
                continue

            # ── L3: 时间衰减 ──
            age = self._age_days(m)
            if age <= 1:
                decay = 1.0
            elif age <= 7:
                decay = 0.9
            elif age <= 30:
                decay = 0.7
            else:
                decay = 0.5

            # 被召回过的记忆有加成
            recall_bonus = min(0.3, m.get("recall_count", 0) * 0.1)

            final = base * decay + recall_bonus
            scored.append((final, m))

        # 对检索到的数据进行按评分进行排序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored]

    # ── 兼容接口 ───────────────────────────────

    def search(self, keyword: str) -> str:
        """旧接口：简单关键词搜索（向后兼容）"""
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

    def format_query_results(self, results: list) -> str:
        """格式化 query() 返回的结果列表，注入 system prompt"""
        if not results:
            return ""
        lines = ["关于用户的相关记忆（按相关性排序）："]
        for m in results[:8]:
            tier = m.get("tier", "")
            tier_label = {"core": "核心", "reference": "参考", "peripheral": "边缘"}.get(tier, "")
            lines.append(f"- [{tier_label}] {m['content']} ({m.get('created_at', '')})")
        return "\n".join(lines)

    def mark_recalled(self, keyword: str):
        """标记已召回的记忆，增加 recall_count"""
        self._load()
        keyword_lower = keyword.lower()
        for m in self._cache:
            if keyword_lower in m.get("content", "").lower():
                m["recall_count"] = m.get("recall_count", 0) + 1
        self._flush()

    def __len__(self):
        self._load()
        return len(self._cache)
