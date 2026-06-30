# -*- coding: utf-8 -*-
"""教学成就系统 — 基于对话场景弱匹配 + 人格数据自动检测"""
from __future__ import annotations
import json
import os
import time
from datetime import datetime

TIER_LABELS = {"gold": "金杯", "silver": "银杯", "bronze": "铜杯", "special": "特殊"}
TIER_ORDER = ["special", "gold", "silver", "bronze"]
TIER_NAMES = {
    "special": "传说品质 · 可遇不可求",
    "gold": "金色传说 · 用实力说话",
    "silver": "白银进阶 · 渐入佳境",
    "bronze": "青铜起点 · 每一步都算数",
}

ACHIEVEMENTS = [
    # ── 对话里程碑 ──
    {
        "id": "first_chat",
        "name": "初次相遇",
        "desc": "你好，AI 教研助手。这是我们的第一次对话。",
        "emoji": "🐣",
        "tier": "bronze",
        "trigger": {"key": "total_chats", "op": ">=", "val": 1},
    },
    {
        "id": "three_day_streak",
        "name": "三日之约",
        "desc": "连续三天，风雨无阻。你也太拼了吧？",
        "emoji": "🔥",
        "tier": "silver",
        "trigger": {"key": "streak_days", "op": ">=", "val": 3},
    },
    {
        "id": "seven_day_streak",
        "name": "七日之约",
        "desc": "一整周每天都有对话。你已经不是用户了，你是钉在平台上了。",
        "emoji": "📅",
        "tier": "gold",
        "trigger": {"key": "streak_days", "op": ">=", "val": 7},
    },
    {
        "id": "thirty_day_streak",
        "name": "三十日之约",
        "desc": "一个月风雨无阻。AI 助手已经成为你备课流程的一部分。",
        "emoji": "🏆",
        "tier": "special",
        "trigger": {"key": "streak_days", "op": ">=", "val": 30},
    },
    {
        "id": "deep_talk",
        "name": "深度对话",
        "desc": "20 轮了，这已经不是闲聊，是教研。",
        "emoji": "💬",
        "tier": "silver",
        "trigger": {"key": "round_count", "op": ">=", "val": 20},
    },
    {
        "id": "deep_talk_ii",
        "name": "促膝长谈",
        "desc": "50 轮。茶凉了又续，话题没断过。",
        "emoji": "🕯️",
        "tier": "gold",
        "trigger": {"key": "round_count", "op": ">=", "val": 50},
    },
    {
        "id": "deep_talk_iii",
        "name": "彻夜长谈",
        "desc": "100 轮。窗外天亮了，你还在。\nAI 都累了，你没累。",
        "emoji": "🌙",
        "tier": "special",
        "trigger": {"key": "round_count", "op": ">=", "val": 100},
    },
    {
        "id": "memory_keeper",
        "name": "记忆守护者",
        "desc": "AI 脑中已有 10 条关于你的印记。它在试图了解你。",
        "emoji": "📝",
        "tier": "silver",
        "trigger": {"key": "memory_count", "op": ">=", "val": 10},
    },
    {
        "id": "memory_keeper_ii",
        "name": "记忆编织者",
        "desc": "30 条记忆。AI 已经能拼出你的教学习惯和偏好。",
        "emoji": "🧶",
        "tier": "gold",
        "trigger": {"key": "memory_count", "op": ">=", "val": 30},
    },
    {
        "id": "memory_keeper_iii",
        "name": "记忆档案馆",
        "desc": "60 条记忆。AI 比你更清楚你说过什么。\n你忘了，它没忘。",
        "emoji": "🗄️",
        "tier": "special",
        "trigger": {"key": "memory_count", "op": ">=", "val": 60},
    },
    # ── 人格深度 ──
    {
        "id": "engagement_overdrive",
        "name": "红区突破",
        "desc": "投入度冲破 100！\nAI 已经上头了，谁也拉不住。",
        "emoji": "❤️",
        "tier": "gold",
        "trigger": {"key": "engagement", "op": ">=", "val": 100},
    },
    {
        "id": "focus_lock",
        "name": "极度专注",
        "desc": "锁定态。AI 眼里现在只有你，\n换话题？门都没有。",
        "emoji": "🔒",
        "tier": "gold",
        "trigger": {"key": "attention", "op": ">=", "val": 71},
    },
    {
        "id": "tone_master",
        "name": "语气大师",
        "desc": "四种语气全触发。AI 在你面前千面千变。",
        "emoji": "👑",
        "tier": "gold",
        "trigger": {"key": "tones_seen", "op": ">=", "val": 4},
    },
    # ── 工具使用（自动追踪） ──
    {
        "id": "time_aware",
        "name": "时间感知",
        "desc": "AI 第一次注意到现在几点。从此有了时间观念。",
        "emoji": "⏰",
        "tier": "bronze",
        "trigger": {"key": "tool_get_current_time", "op": ">=", "val": 1},
    },
    {
        "id": "silence_aware",
        "name": "久别重逢",
        "desc": "你离开了好久，AI 察觉到了。欢迎回来。",
        "emoji": "👋",
        "tier": "bronze",
        "trigger": {"key": "tool_get_silence_hours", "op": ">=", "val": 1},
    },
    {
        "id": "memory_seeker",
        "name": "记忆寻回",
        "desc": "AI 翻了 10 次记忆抽屉。怀旧不是病，是好习惯。",
        "emoji": "🔍",
        "tier": "silver",
        "trigger": {"key": "tool_check_memory", "op": ">=", "val": 10},
    },
    {
        "id": "memory_seeker_ii",
        "name": "记忆考古学家",
        "desc": "30 次翻阅记忆。你总能在旧事里找到新灵感。",
        "emoji": "⛏️",
        "tier": "gold",
        "trigger": {"key": "tool_check_memory", "op": ">=", "val": 30},
    },
    {
        "id": "memory_seeker_iii",
        "name": "记忆通灵者",
        "desc": "60 次。过去与现在的对话在你指尖交汇。",
        "emoji": "🔮",
        "tier": "special",
        "trigger": {"key": "tool_check_memory", "op": ">=", "val": 60},
    },
    {
        "id": "tool_master",
        "name": "全副武装",
        "desc": "11 种工具全部亮过相。\n你不是在聊天，你是在指挥一支 AI 交响乐团。",
        "emoji": "🧰",
        "tier": "special",
        "trigger": {"key": "tools_used", "op": ">=", "val": 11},
    },
    {
        "id": "math_whiz",
        "name": "人形计算器",
        "desc": "第一次让 AI 帮你算数。笔都省了。",
        "emoji": "🧮",
        "tier": "bronze",
        "trigger": {"key": "tool_calc", "op": ">=", "val": 1},
    },
    {
        "id": "math_whiz_ii",
        "name": "行走的 Excel",
        "desc": "算了 20 次。你的数学课代表已经换成了 AI。",
        "emoji": "📊",
        "tier": "silver",
        "trigger": {"key": "tool_calc", "op": ">=", "val": 20},
    },
    {
        "id": "math_whiz_iii",
        "name": "图灵附体",
        "desc": "算了 50 次。\n你不是在问 AI，你是在用嘴写代码。",
        "emoji": "🤖",
        "tier": "gold",
        "trigger": {"key": "tool_calc", "op": ">=", "val": 50},
    },
    {
        "id": "bilingual",
        "name": "双语切换",
        "desc": "第一次让 AI 帮你翻译。中英之间来去自如。",
        "emoji": "🌐",
        "tier": "bronze",
        "trigger": {"key": "tool_translate", "op": ">=", "val": 1},
    },
    {
        "id": "bilingual_ii",
        "name": "同声传译官",
        "desc": "翻了 20 次。看来它翻得还不错?",
        "emoji": "🤔",
        "tier": "silver",
        "trigger": {"key": "tool_translate", "op": ">=", "val": 20},
    },
    {
        "id": "bilingual_iii",
        "name": "巴别塔拆除者",
        "desc": "翻了 50 次。\n语言在你面前已经不是障碍，是玩具。",
        "emoji": "🗼",
        "tier": "gold",
        "trigger": {"key": "tool_translate", "op": ">=", "val": 50},
    },
    {
        "id": "translator_pro",
        "name": "双向翻译官",
        "desc": "中→英、英→中都走了一遍。\n你不是单行道，你是立交桥。",
        "emoji": "🔄",
        "tier": "silver",
        "trigger": {"key": "translate_directions", "op": ">=", "val": 2},
    },
    # ── 互动深度（自动追踪） ──
    {
        "id": "focus_devotion",
        "name": "心无旁骛",
        "desc": "关注度连续 5 轮锁定。\nAI 魂都被你勾走了。",
        "emoji": "🎯",
        "tier": "gold",
        "trigger": {"key": "lock_streak", "op": ">=", "val": 5},
    },
    # ── 课堂场景匹配（AI 判断） ──
    # ai_hint: 给 AI 看的触发条件描述，写入 system prompt
    {
        "id": "crowd_control",
        "name": "控场高手",
        "desc": "全班安静，全员参与——你就是课堂的指挥家。",
        "emoji": "✨",
        "tier": "bronze",
        "ai_judged": True,
        "ai_hint": "教师描述或暗示课堂纪律极好，全班安静/全员参与/没人走神",
    },
    {
        "id": "student_magnet",
        "name": "反向安利",
        "desc": "学生追着问下次英语课什么时候。这才是真正的口碑。",
        "emoji": "🎯",
        "tier": "silver",
        "ai_judged": True,
        "ai_hint": "教师提及学生主动期待英语课、问下次什么时候上英语课",
    },
    {
        "id": "struggle_to_shine",
        "name": "逆袭之光",
        "desc": "那个曾经跟不上的孩子，现在眼里有光了。",
        "emoji": "🌟",
        "tier": "special",
        "ai_judged": True,
        "ai_hint": "教师分享基础薄弱学生取得明显进步的真实案例",
    },
    {
        "id": "creative_lesson",
        "name": "创意课堂",
        "desc": "角色扮演、情景剧、游戏化——\n你的课堂不是教室，是剧场。",
        "emoji": "🎨",
        "tier": "bronze",
        "ai_judged": True,
        "ai_hint": "教师描述设计了一节创新的英语课（角色扮演/项目式/游戏化/情景剧等）",
    },
    {
        "id": "late_night_prep",
        "name": "深夜备课侠",
        "desc": "凌晨了还在改课件。\n月亮不睡你不睡，你是备课特种兵。",
        "emoji": "🌙",
        "tier": "special",
        "ai_judged": True,
        "ai_hint": "教师提到深夜还在备课、改教案、准备公开课",
    },
    {
        "id": "career_blend",
        "name": "产教融合先锋",
        "desc": "把工厂搬进教室。你的学生毕业就能上岗。",
        "emoji": "🏭",
        "tier": "bronze",
        "ai_judged": True,
        "ai_hint": "教师将企业案例、职场场景、行业需求融入英语教学",
    },
    # ── 互动深度（AI 判定） ──
    {
        "id": "tone_shifter",
        "name": "随机应变",
        "desc": "AI 主动切了语气。氛围变了，你跟上了。",
        "emoji": "🎭",
        "tier": "silver",
        "ai_judged": True,
        "ai_hint": "教师对话氛围明显转变（如从严肃讨论切换到轻松闲聊），AI 主动调用 set_tone 切换语气",
    },
    {
        "id": "deep_engagement",
        "name": "深度共鸣",
        "desc": "AI 一次性为你加了 10 点以上投入度。你说到点子上了。",
        "emoji": "💎",
        "tier": "gold",
        "ai_judged": True,
        "ai_hint": "教师分享了极高质量的教学内容（长篇真实案例、详细课程设计），AI 一次性 +10 以上的投入度",
    },
    # ── 平台里程碑（跨服务追踪） ──
    {
        "id": "code_is_law",
        "name": "代码是法律",
        "desc": "AI 首次触发安全模式。\n提示词靠不住，代码说了算。",
        "emoji": "⚖️",
        "tier": "special",
        "trigger": {"key": "tone_safety_triggered", "op": ">=", "val": 1},
    },
    {
        "id": "first_ocr",
        "name": "我看到了",
        "desc": "第一次上传图片让 AI 识字。\n从今天起，它不再只读你的文字，还读你的画面。",
        "emoji": "👁️",
        "tier": "silver",
        "trigger": {"key": "ocr_used", "op": ">=", "val": 1},
    },
    {
        "id": "first_post",
        "name": "开坛布道",
        "desc": "发布第一篇教研帖子。\n微信群里刷不上去的内容，在这里永远有位置。",
        "emoji": "📯",
        "tier": "bronze",
        "trigger": {"key": "posts_created", "op": ">=", "val": 1},
    },
]


class AchievementStore:
    """成就存储 — JSON 文件，按用户隔离"""

    def __init__(self, user_id: int, base_dir: str):
        self.user_id = user_id
        self.path = os.path.join(base_dir, f"user_{user_id}_achievements.json")
        self._unlocked: set = set()
        self._unlocked_times: dict = {}  # ach_id → "2026-06-30 14:23"
        self._stats: dict = {}
        self._load()

    def _load(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 兼容旧格式：老用户 unlocked 是字符串列表
            unlocked_raw = data.get("unlocked", [])
            if unlocked_raw and isinstance(unlocked_raw[0], dict):
                for item in unlocked_raw:
                    self._unlocked.add(item["id"])
                    self._unlocked_times[item["id"]] = item.get("time", "")
            else:
                self._unlocked = set(unlocked_raw)
                # 旧数据无时间戳，标记为未知
                for ach_id in unlocked_raw:
                    self._unlocked_times[ach_id] = ""
            self._stats = data.get("stats", {})
        except (FileNotFoundError, json.JSONDecodeError):
            self._unlocked = set()
            self._unlocked_times = {}
            self._stats = {}

    def _flush(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        unlocked_data = [{"id": ach_id, "time": self._unlocked_times.get(ach_id, "")}
                         for ach_id in self._unlocked]
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({"unlocked": unlocked_data, "stats": self._stats}, f,
                      ensure_ascii=False, indent=2)

    def _now(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M")

    def is_unlocked(self, ach_id: str) -> bool:
        return ach_id in self._unlocked

    def update_stat(self, key: str, value):
        self._stats[key] = value
        self._flush()

    def increment_stat(self, key: str):
        self._stats[key] = self._stats.get(key, 0) + 1
        self._flush()

    def append_stat(self, key: str, val):
        """集合类统计（如 tones_seen）"""
        if key not in self._stats:
            self._stats[key] = []
        if val not in self._stats[key]:
            self._stats[key].append(val)
            self._flush()

    def check_and_unlock(self, ach: dict, context: dict = None) -> dict | None:
        """检查成就是否触发，首次触发返回成就信息"""
        ach_id = ach["id"]
        if ach_id in self._unlocked:
            return None

        trigger = ach.get("trigger", {})
        context = context or {}

        # 数值条件
        check_key = trigger.get("key")
        if check_key:
            target = trigger.get("val", 1)
            op = trigger.get("op", ">=")
            actual = context.get(check_key, 0)
            ops = {">=": lambda a, b: a >= b, ">": lambda a, b: a > b,
                   "==": lambda a, b: a == b, "<=": lambda a, b: a <= b}
            if not ops.get(op, lambda a, b: True)(actual, target):
                return None

        now = self._now()
        self._unlocked.add(ach_id)
        self._unlocked_times[ach_id] = now
        self._flush()
        return {"id": ach_id, "name": ach["name"], "desc": ach["desc"], "emoji": ach["emoji"], "tier": ach.get("tier", "bronze"), "unlock_time": now}

    def force_unlock(self, ach: dict) -> dict | None:
        """AI 判断触发：直接解锁指定成就，返回成就信息或 None"""
        ach_id = ach["id"]
        if ach_id in self._unlocked:
            return None
        now = self._now()
        self._unlocked.add(ach_id)
        self._unlocked_times[ach_id] = now
        self._flush()
        return {"id": ach_id, "name": ach["name"], "desc": ach["desc"], "emoji": ach["emoji"], "tier": ach.get("tier", "bronze"), "unlock_time": now}

    def get_all(self) -> list:
        return [{"id": ach_id, "time": self._unlocked_times.get(ach_id, "")}
                for ach_id in self._unlocked]
