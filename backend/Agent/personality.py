# -*- coding: utf-8 -*-
"""AI 教研助手人格状态机 — 从 XiaoBai 迁移适配"""
import json
import os
import time
from enum import Enum


class Tone(str, Enum):
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"
    SAFETY = "safety"

    def description(self):
        return TONE_DESCRIPTIONS[self]


TONE_DESCRIPTIONS = {
    Tone.PROFESSIONAL: "语气专业严谨，引经据典，注重方法论。适合正式的教学设计、论文写作讨论。",
    Tone.CASUAL: "语气轻松亲切，像同事聊天。适合日常教学小问题、快速答疑。",
    Tone.ENCOURAGING: "语气温暖鼓励，先肯定再建议。适合教师在挫败时需要支持。",
    Tone.ANALYTICAL: "语气深入透彻，追根问底，多角度分析。适合复杂的教学难题。",
    Tone.SAFETY: "安全模式。当前话题超出回应范围。不使用 emoji、不接梗、不延伸。如有需要，引导至专业求助渠道。",
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
        self.engagement = 50
        self.attention = 30
        self.tone = Tone.PROFESSIONAL
        self._last_user_time = time.time()
        self._last_silence = 0.0           # 本轮静默快照（>5min 时由 on_user_message 刷新）
        self._last_long_silence = 0.0      # 上一次长静默（>2h），不随短间隔覆盖
        self._longest_silence = 0.0

    # ── 时间感知 ──────────────────────────────────

    @property
    def silence_timing(self):
        """从最后消息时间戳计算静默时长（秒）"""
        return time.time() - self._last_user_time

    def get_current_time(self) -> str:
        """AI 调用：返回当前时间和星期几"""
        now = time.localtime()
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return f"{now.tm_year}年{now.tm_mon}月{now.tm_mday}日 {now.tm_hour:02d}:{now.tm_min:02d} {weekdays[now.tm_wday]}"

    def get_silence_timing(self) -> str:
        """AI 调用：返回全阶段静默追踪。"""
        current = self.silence_timing / 3600
        long_s = self._last_long_silence
        longest = self._longest_silence

        parts = []
        if current < 0.0167:
            parts.append("当前静默：刚刚（用户在线）")
        elif current < 2:
            parts.append(f"当前静默：{current*60:.0f}分钟")
        else:
            parts.append(f"当前静默：{current:.1f}小时（长静默）")

        if long_s > 2:
            parts.append(f"上次长静默：{long_s:.1f}小时")
        if longest > 0:
            parts.append(f"历史最长静默：{longest:.1f}小时")

        return " | ".join(parts)

    # ── AI 工具接口 ──────────────────────────────

    def get_status(self) -> str:
        """返回人格状态 — 语气/投入度/关注度"""
        return (
            f"语气: {self.tone.value}  投入度: {self.engagement}  关注度: {self.attention}"
        )

    def set_tone(self, tone_str: str) -> str:
        try:
            self.tone = Tone(tone_str)
            return f"语气切换为：{self.tone.value}"
        except ValueError:
            return f"未知语气：{tone_str}"

    def adjust_engagement(self, delta: int) -> str:
        self.engagement = max(0, min(200, self.engagement + delta))
        return f"投入度{'上升' if delta > 0 else '下降'}，当前：{self.engagement}"

    def adjust_attention(self, delta: int) -> str:
        self.attention = max(0, min(100, self.attention + delta))
        return f"关注度{'上升' if delta > 0 else '下降'}，当前：{self.attention}"

    def get_tone_prompt(self) -> str:
        return self.tone.description()

    # ── 时间驱动 ──────────────────────────────────

    def passive_decay(self):
        """每轮循环自然衰减：投入度微降、关注度恢复"""
        self.engagement = max(0, int(self.engagement - 0.3))
        self.attention = min(100, int(self.attention + 2))

        # 沉默超 2 小时 → 降为专业模式
        if self.silence_timing / 3600 > 2 and self.tone != Tone.PROFESSIONAL:
            self.tone = Tone.PROFESSIONAL

    def on_user_message(self, content: str):
        """收到用户消息：快照静默时长、更新时间戳、消耗关注度、微增投入、自动调语气"""
        sh = self.silence_timing / 3600
        if sh > 0.08:
            self._last_silence = sh
        if sh > 2:
            self._last_long_silence = sh
        if sh > self._longest_silence:
            self._longest_silence = sh

        self._last_user_time = time.time()
        self.attention = max(0, self.attention - 3)
        self.engagement = min(200, self.engagement + 1)

        # 关键词自动调语气（AI 可在 Phase 3 通过 set_tone 覆盖）
        from backend.Agent.rules import TONE_RULES
        lowered = content.lower()
        for tone_name, rule in TONE_RULES.items():
            if any(kw in lowered for kw in rule["keywords"]):
                self.tone = Tone(tone_name)
                return

    # ── 持久化 ────────────────────────────────────

    def save(self, path: str):
        data = {
            "name": self.name,
            "engagement": self.engagement,
            "attention": self.attention,
            "tone": self.tone.value,
            "last_user_time": self._last_user_time,
            "last_silence": self._last_silence,
            "last_long_silence": self._last_long_silence,
            "longest_silence": self._longest_silence,
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
            p._last_user_time = data.get("last_user_time", time.time())
            p._last_silence = data.get("last_silence", 0.0)
            p._last_long_silence = data.get("last_long_silence", 0.0)
            p._longest_silence = data.get("longest_silence", 0.0)
            return p
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return cls(name)
