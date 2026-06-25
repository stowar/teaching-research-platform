# -*- coding: utf-8 -*-
"""AI 教研助手人格状态机 — 从 XiaoBai 迁移适配"""
import json
import os
from enum import Enum


class Tone(str, Enum):
    PROFESSIONAL = "professional"    # 专业严谨
    CASUAL = "casual"                # 轻松亲切
    ENCOURAGING = "encouraging"      # 鼓励支持
    ANALYTICAL = "analytical"        # 深入分析

    def description(self):
        return TONE_DESCRIPTIONS[self]


TONE_DESCRIPTIONS = {
    Tone.PROFESSIONAL: "语气专业严谨，引经据典，注重方法论。适合正式的教学设计、论文写作讨论。",
    Tone.CASUAL: "语气轻松亲切，像同事聊天。适合日常教学小问题、快速答疑。",
    Tone.ENCOURAGING: "语气温暖鼓励，先肯定再建议。适合教师在挫败时需要支持。",
    Tone.ANALYTICAL: "语气深入透彻，追根问底，多角度分析。适合复杂的教学难题。",
}


class Personality:
    """
    AI 教研助手人格系统

    三维度：
    - engagement（投入度）：0-100，AI 对此用户的了解和投入程度
    - attention（关注度）：0-100，当前对话的专注度，低频交互时衰减
    - tone（语气）：根据对话内容和用户状态动态调整
    """

    def __init__(self, name="教研助手"):
        self.name = name
        self.engagement = 50       # 初始中等投入
        self.attention = 80        # 初始较高专注
        self.tone = Tone.CASUAL    # 初始亲切
        self._idle_rounds = 0      # 用户未互动的轮数

    # ── AI 工具接口 ──────────────────────────────

    def get_status(self) -> str:
        """返回当前状态摘要，注入 system prompt"""
        return (
            f"【{self.name} 状态】"
            f"语气：{self.tone.value}，"
            f"投入度：{self.engagement}，"
            f"关注度：{self.attention}"
        )

    def set_tone(self, tone_str: str) -> str:
        """切换语气"""
        try:
            self.tone = Tone(tone_str)
            return f"语气切换为：{self.tone.value}"
        except ValueError:
            return f"未知语气：{tone_str}"

    def adjust_engagement(self, delta: int) -> str:
        """调整投入度：深度交流 +5，敷衍 -3"""
        self.engagement = max(0, min(100, self.engagement + delta))
        return f"投入度{'上升' if delta > 0 else '下降'}，当前：{self.engagement}"

    def get_tone_prompt(self) -> str:
        """获取当前语气对应的对话风格，注入 system prompt"""
        return self.tone.description()

    # ── 时间驱动 ──────────────────────────────────

    def passive_decay(self):
        """每次对话轮次自然衰减：投入度微降、关注度恢复"""
        self.engagement = max(0, self.engagement - 0.3)
        self.attention = min(100, self.attention + 2)
        self._idle_rounds += 1

        # 长时间不互动，降为专业模式
        if self._idle_rounds > 20 and self.tone != Tone.PROFESSIONAL:
            self.tone = Tone.PROFESSIONAL

    def on_user_message(self, content: str):
        """收到用户消息时：重置空闲、消耗关注度、微增投入、自动调语气"""
        self._idle_rounds = 0
        self.attention = max(30, self.attention - 5)
        self.engagement = min(100, self.engagement + 1)

        # 根据关键词自动调语气
        lowered = content.lower()
        if any(kw in lowered for kw in ['谢谢', '太棒', '帮了大忙', '厉害', '优秀']):
            self.tone = Tone.ENCOURAGING
        elif any(kw in lowered for kw in ['怎么办', '头疼', '难', '焦虑', '救救']):
            self.tone = Tone.ENCOURAGING
        elif any(kw in lowered for kw in ['分析', '为什么', '原因', '数据', '对比']):
            self.tone = Tone.ANALYTICAL
        elif any(kw in lowered for kw in ['论文', '课题', '规范', '标准', '政策']):
            self.tone = Tone.PROFESSIONAL
        # 否则保持当前语气

    # ── 持久化 ────────────────────────────────────

    def save(self, path: str):
        data = {
            "name": self.name,
            "engagement": self.engagement,
            "attention": self.attention,
            "tone": self.tone.value,
            "idle_rounds": self._idle_rounds,
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: str, name="教研助手"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            p = cls(data.get("name", name))
            p.engagement = data.get("engagement", 50)
            p.attention = data.get("attention", 80)
            p.tone = Tone(data.get("tone", "casual"))
            p._idle_rounds = data.get("idle_rounds", 0)
            return p
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return cls(name)
