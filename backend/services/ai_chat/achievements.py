# -*- coding: utf-8 -*-
"""成就检测"""
from __future__ import annotations

import time

from backend.db import ai_chat_db
from backend.Agent.personality import Personality
from backend.Agent.memory import MemoryStore
from backend.Agent.achievements import AchievementStore, ACHIEVEMENTS
from backend.schema.vo.ai_chat import AchievementVO
from .helpers import AI_DATA_DIR


def compute_streak(store: AchievementStore) -> int:
    today = time.strftime("%Y-%m-%d")
    last = store._stats.get("last_active_date", "")
    streak = store._stats.get("streak_days", 0)
    if last == today:
        return streak
    yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
    streak = streak + 1 if last == yesterday else 1
    store._stats["last_active_date"] = today
    store._stats["streak_days"] = streak
    store._flush()
    return streak


def check_achievements(user_id: int, user_message: str, personality: Personality,
                       memory: MemoryStore, conversation_id: int) -> list:
    store = AchievementStore(user_id, AI_DATA_DIR)
    store.increment_stat("total_chats")
    streak = compute_streak(store)
    round_count = ai_chat_db.get_message_count(conversation_id)
    store.append_stat("tones_seen", personality.tone.value)

    if personality.attention >= 71:
        store.increment_stat("lock_streak")
    else:
        store._stats["lock_streak"] = 0
        store._flush()

    context = {
        "user_message": user_message,
        "total_chats": store._stats.get("total_chats", 0),
        "streak_days": streak,
        "round_count": round_count,
        "memory_count": len(memory),
        "engagement": personality.engagement,
        "attention": personality.attention,
        "tones_seen": len(store._stats.get("tones_seen", [])),
        "tools_used": len(store._stats.get("tools_used", [])),
        "tool_get_current_time": store._stats.get("tool_get_current_time", 0),
        "tool_get_silence_hours": store._stats.get("tool_get_silence_hours", 0),
        "tool_check_memory": store._stats.get("tool_check_memory", 0),
        "tool_calc": store._stats.get("tool_calc", 0),
        "tool_translate": store._stats.get("tool_translate", 0),
        "translate_directions": len(store._stats.get("translate_directions", [])),
        "tone_safety_triggered": store._stats.get("tone_safety_triggered", 0),
        "ocr_used": store._stats.get("ocr_used", 0),
        "lock_streak": store._stats.get("lock_streak", 0),
    }

    new_achievements = []
    for ach in ACHIEVEMENTS:
        if ach.get("ai_judged"):
            continue
        r = store.check_and_unlock(ach, context)
        if r:
            new_achievements.append(AchievementVO(
                id=r["id"], name=r["name"], desc=r["desc"], emoji=r["emoji"],
                tier=r.get("tier", "bronze"), unlock_time=r.get("unlock_time", ""),
            ))
    return new_achievements
