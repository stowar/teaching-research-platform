# -*- coding: utf-8 -*-
"""AI 聊天室服务 — 对话逻辑 + 状态机 + 记忆系统"""
import base64
import io
import json
import os
import time
import re

from backend.domain.ai_chat import IAIChatService
from backend.db import ai_chat_db
from backend.core.exceptions import BusinessException
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.ai_chat import (
    ConversationVO, ConversationDetailVO, MessageVO, ChatReplyVO, AIStateVO, AchievementVO,
    to_conversation_vo, to_message_vo,
)
from backend.Agent.provider import get_ai_provider
from backend.Agent.personality import Personality
from backend.Agent.memory import MemoryStore
from backend.Agent.tools import TOOLS, build_tool_map
from backend.Agent.rules import build_system_prompt, MAX_CONTEXT_MESSAGES, MAX_TOOL_ROUNDS, MAX_MESSAGES_PER_DAY, SUMMARIZE_THRESHOLD, KEEP_LAST, DEFAULT_MODEL
from backend.Agent.achievements import AchievementStore, ACHIEVEMENTS
from backend.core.config import settings

# 记忆文件存储目录
AI_DATA_DIR = os.path.join(settings.BASE_DIR, "backend", "data", "ai")


def _is_unlocked(user_id: int) -> bool:
    """检查用户本日是否已被管理员解锁"""
    try:
        with open(os.path.join(AI_DATA_DIR, "quota_override.json"), "r") as f:
            overrides = json.load(f)
        return overrides.get(str(user_id)) == time.strftime("%Y-%m-%d")
    except (FileNotFoundError, json.JSONDecodeError):
        return False


def _process_image(data_url: str) -> str:
    """解码 base64 图片，OCR 提取文字"""
    try:
        # 解析 data:image/png;base64,xxxx
        match = re.match(r"data:image/\w+;base64,(.+)", data_url)
        if not match:
            return ""
        img_bytes = base64.b64decode(match.group(1))

        # 尝试 PIL 读尺寸
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(img_bytes))
            w, h = img.size
            meta = f"[图片: {img.format or '?'}, {w}x{h}]"
        except Exception:
            meta = "[图片上传成功]"

        # 尝试 OCR
        ocr_text = ""
        try:
            import pytesseract
            img_ocr = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(img_ocr, lang="chi_sim+eng").strip()
        except Exception:
            try:
                import easyocr
                reader = easyocr.Reader(["ch_sim", "en"], gpu=False, verbose=False)
                results = reader.readtext(img_bytes)
                ocr_text = " ".join(r[1] for r in results)
            except Exception:
                pass

        if ocr_text:
            return f"{meta}\n识别文字：\n{ocr_text}"
        return meta
    except Exception:
        return "[图片解析失败]"
    """检查用户本日是否已被管理员解锁"""
    try:
        with open(os.path.join(AI_DATA_DIR, "quota_override.json"), "r") as f:
            overrides = json.load(f)
        return overrides.get(str(user_id)) == time.strftime("%Y-%m-%d")
    except (FileNotFoundError, json.JSONDecodeError):
        return False

TONE_LABELS = {
    "professional": "专业模式",
    "casual": "轻松模式",
    "encouraging": "鼓励模式",
    "analytical": "分析模式",
    "safety": "安全模式",
}


def _summarize_and_trim(system_msg, history, memory, model):
    """
    对话过长时的分层裁切总结（从 XiaoBai 迁移）：
    - 超过阈值的历史消息 → AI 总结为一段摘要 → 写入长期记忆
    - 保留最近 KEEP_LAST 条在上下文窗口
    """
    total = len(system_msg) + len(history)
    if total <= SUMMARIZE_THRESHOLD:
        return history

    # 取要被总结掉的部分
    to_summarize = history[:-KEEP_LAST] if len(history) > KEEP_LAST else history
    if len(to_summarize) < 10:
        return history[-KEEP_LAST:]

    lines = []
    for m in to_summarize:
        role = m.get("role", "")
        content = m.get("content", "") or ""
        if role in ("user", "assistant") and content:
            tag = "教师" if role == "user" else "AI助手"
            lines.append(f"{tag}: {content}")

    if not lines:
        return history[-KEEP_LAST:]

    try:
        provider = get_ai_provider(model)
        summary_resp = provider.chat([{
            "role": "user",
            "content": "把以下对话总结为一段话（100字以内，不要换行）：\n" + "\n".join(lines)
        }])
        summary = summary_resp.get("content", "").strip()
        if summary:
            memory.add(f"[对话摘要] {summary}", "experience")
    except Exception:
        pass

    return history[-KEEP_LAST:]


def _enforce_silence(personality):
    """沉默超过 2 小时：投入度 -2/小时、关注度重置为发散态"""
    h = personality.silence_hours
    if h > 2:
        decay = int(h * 2)
        personality.engagement = max(0, personality.engagement - decay)
        personality.attention = min(30, personality.attention)


def _enforce_attention(messages, personality, engagement_before):
    """AI 没调 adjust_attention 时，联动投入度变化推断关注度"""
    for msg in messages:
        tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else None
        if tool_calls:
            for tc in tool_calls:
                if tc.get("function", {}).get("name") == "adjust_attention":
                    return

    # 投入度涨了 → 对话质量高 → 聚焦 +5；投入度跌了 → 敷衍 → 发散 -5
    delta = 5 if personality.engagement > engagement_before else -5
    personality.adjust_attention(delta)


def _enforce_engagement(messages, personality, user_message):
    """AI 没调 adjust_engagement 时，代码强制执行。提示词靠不住，代码靠得住。"""
    called = False
    for msg in messages:
        tool_calls = msg.get("tool_calls") if isinstance(msg, dict) else None
        if tool_calls:
            for tc in tool_calls:
                fn = tc.get("function", {})
                if fn.get("name") == "adjust_engagement":
                    called = True
                    break
        if called:
            break

    if called:
        return

    # 根据用户消息长度和内容推断 delta
    delta = _infer_delta(user_message)
    personality.adjust_engagement(delta)


def _infer_delta(message: str) -> int:
    """根据消息内容推断投入度变化值"""
    length = len(message)
    if length <= 3:
        return -3    # 单字/表情 → 敷衍
    if length > 100:
        return 5     # 长消息 → 高质量分享
    if length > 20:
        return 3     # 中等 → 追问/探讨
    return 2         # 短消息 → 正常互动


def _mark_recalled_from_response(ai_content: str, user_message: str, memory):
    """检测 AI 回复是否引用了记忆（出现【根据你之前的信息】），标记召回"""
    if "【根据你之前的信息】" in ai_content or "根据你之前的" in ai_content:
        # 从用户消息中提取关键词来标记召回的记忆
        keywords = ["研究方向", "偏好", "课程", "教学", "学生", "班级", "公开课", "教案",
                    "写作", "听说", "阅读", "词汇", "任务驱动", "小组", "考试", "教研"]
        for kw in keywords:
            if kw in user_message or kw in ai_content:
                memory.mark_recalled(kw)


def _tone_label(tone):
    return TONE_LABELS.get(tone.value if hasattr(tone, 'value') else tone, "未知")


def _compute_streak(store: AchievementStore):
    """计算连续活跃天数"""
    today = time.strftime("%Y-%m-%d")
    last = store._stats.get("last_active_date", "")
    streak = store._stats.get("streak_days", 0)

    if last == today:
        return streak

    yesterday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
    if last == yesterday:
        streak += 1
    else:
        streak = 1

    store._stats["last_active_date"] = today
    store._stats["streak_days"] = streak
    store._flush()
    return streak


def _check_achievements(user_id: int, user_message: str, personality, memory,
                        conversation_id: int) -> list:
    """检查并解锁成就，返回新解锁的成就列表"""
    store = AchievementStore(user_id, AI_DATA_DIR)

    # 更新统计
    store.increment_stat("total_chats")

    # 连续天数
    streak = _compute_streak(store)

    # 本轮消息数
    round_count = ai_chat_db.get_message_count(conversation_id)

    # 语气集合
    store.append_stat("tones_seen", personality.tone.value)

    # 关注度锁定连胜
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
        "lock_streak": store._stats.get("lock_streak", 0),
    }

    new_achievements = []
    for ach in ACHIEVEMENTS:
        if ach.get("ai_judged"):
            continue  # AI 自主判断，不由代码自动触发
        result = store.check_and_unlock(ach, context)
        if result:
            new_achievements.append(AchievementVO(
                id=result["id"],
                name=result["name"],
                desc=result["desc"],
                emoji=result["emoji"],
                tier=result.get("tier", "bronze"),
                unlock_time=result.get("unlock_time", ""),
            ))

    return new_achievements


class AIChatService(IAIChatService):

    # ===================== 会话管理 =====================

    def get_conversations(self, user_id):
        conversations = ai_chat_db.get_conversations_by_user(user_id)
        vos = []
        for c in conversations:
            msg_count = getattr(c, 'msg_count', ai_chat_db.get_message_count(c.id))
            vos.append(to_conversation_vo(c, msg_count))
        return ApiResponse(msg="查询成功", data=vos)

    def get_conversation_detail(self, conversation_id, user_id):
        conv = ai_chat_db.get_conversation_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise BusinessException("会话不存在", code=404)
        messages = ai_chat_db.get_messages_by_conversation(conversation_id)
        return ApiResponse(msg="查询成功", data=ConversationDetailVO(
            id=conv.id,
            title=conv.title,
            model=conv.model,
            messages=[to_message_vo(m) for m in messages],
        ))

    def rename_conversation(self, conversation_id, title, user_id):
        conv = ai_chat_db.get_conversation_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise BusinessException("会话不存在", code=404)
        ai_chat_db.rename_conversation_db(conversation_id, title)
        return ApiResponse(msg="重命名成功")

    def delete_conversation(self, conversation_id, user_id):
        conv = ai_chat_db.get_conversation_by_id(conversation_id)
        if not conv or conv.user_id != user_id:
            raise BusinessException("会话不存在", code=404)
        ai_chat_db.delete_conversation_db(conversation_id)
        return ApiResponse(msg="已删除")

    # ===================== AI 状态 =====================

    def get_state(self, user_id, conversation_id: int = None, role: str = "user"):
        if conversation_id:
            personality = Personality.load(
                os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json")
            )
            memory = MemoryStore(conversation_id, AI_DATA_DIR)
        else:
            personality = Personality()
            memory = MemoryStore(0, AI_DATA_DIR)
        today_count = ai_chat_db.count_user_messages_today(user_id)
        limit = "∞" if (role == "admin" or _is_unlocked(user_id)) else MAX_MESSAGES_PER_DAY
        return ApiResponse(msg="查询成功", data=AIStateVO(
            tone=personality.tone.value,
            tone_label=_tone_label(personality.tone),
            engagement=personality.engagement,
            attention=personality.attention,
            silence_hours=round(personality.silence_hours, 1),
            memory_count=len(memory),
            messages_today=today_count,
            messages_limit=limit,
        ))

    # ===================== 成就系统 =====================

    def get_achievements(self, user_id):
        from backend.Agent.achievements import TIER_LABELS, TIER_ORDER, TIER_NAMES
        store = AchievementStore(user_id, AI_DATA_DIR)
        all_unlocked = store.get_all()  # [{id, time}, ...]
        unlocked_map = {item["id"]: item.get("time", "") for item in all_unlocked}
        items = []
        for ach in ACHIEVEMENTS:
            tier = ach.get("tier", "bronze")
            unlocked = ach["id"] in unlocked_map
            items.append({
                "id": ach["id"],
                "name": ach["name"],
                "desc": ach["desc"],
                "emoji": ach["emoji"],
                "tier": tier,
                "tier_label": TIER_LABELS.get(tier, tier),
                "unlock_time": unlocked_map.get(ach["id"], ""),
                "unlocked": unlocked,
            })
        return ApiResponse(msg="查询成功", data={
            "items": items,
            "tier_order": TIER_ORDER,
            "tier_names": TIER_NAMES,
            "tier_labels": TIER_LABELS,
        })

    # ===================== 对话核心逻辑 =====================

    def chat(self, user_id, message, conversation_id=None, model=None, role="user", user_name="", images=None):
        if model is None:
            model = DEFAULT_MODEL
        # ── 0. 每日配额（管理员无限 + 解锁检查） ──
        today_count = ai_chat_db.count_user_messages_today(user_id)
        over_limit = today_count >= MAX_MESSAGES_PER_DAY
        is_unlocked = role == "admin" or _is_unlocked(user_id)
        if over_limit and not is_unlocked:
                return ApiResponse(msg="额度已用完", data=ChatReplyVO(
                conversation_id=conversation_id or 0,
                message=MessageVO(role="assistant", content="今日消息已达上限，请明天再来。", timestamp=0),
            ))

        # ── 1. 会话管理 ──
        if conversation_id:
            conv = ai_chat_db.get_conversation_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise BusinessException("会话不存在", code=404)
        else:
            title = message[:20] + ("..." if len(message) > 20 else "")
            conversation_id = ai_chat_db.create_conversation(user_id, title, model)

        # ── 2. 处理图片 → 保存用户消息 ──
        if images:
            ocr_parts = []
            for img in images:
                ocr = _process_image(img)
                if ocr:
                    ocr_parts.append(ocr)
            if ocr_parts:
                message = f"{message}\n\n" + "\n---\n".join(ocr_parts) if message.strip() else "\n---\n".join(ocr_parts)
        ai_chat_db.create_message(conversation_id, "user", message)

        # ── 3. 加载人格和记忆（按 conversation_id 隔离） ──
        personality = Personality.load(
            os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json")
        )
        _enforce_silence(personality)
        engagement_before = personality.engagement
        personality.on_user_message(message)
        memory = MemoryStore(conversation_id, AI_DATA_DIR)

        # ── 3.5 收集用户状态（嵌入提示词） ──
        ach_store = AchievementStore(user_id, AI_DATA_DIR)
        ach_unlocked = ach_store.get_all()  # [{id, time}, ...]
        ach_unlocked_ids = [item["id"] for item in ach_unlocked]
        ach_names = [a["name"] for a in ACHIEVEMENTS if a["id"] in ach_unlocked_ids]
        user_state = {
            "unlocked_ach": ach_names,
            "unlocked_ach_ids": ach_unlocked_ids,
            "total_ach": len(ACHIEVEMENTS),
            "messages_today": today_count,
            "messages_limit": MAX_MESSAGES_PER_DAY if not is_unlocked else "∞",
            "streak_days": ach_store._stats.get("streak_days", 0),
            "memory_count": len(memory),
            "is_admin": role == "admin",
            "is_unlocked": is_unlocked and role != "admin",
        }

        # ── 4. 构建消息上下文 ──
        system_prompt = build_system_prompt(personality, memory, user_name, user_state)
        messages = [{"role": "system", "content": system_prompt}]
        history = ai_chat_db.get_messages_by_conversation(conversation_id)
        # 只加载 user/assistant 消息，跳过 tool 和空 content
        history = [{"role": m.role, "content": m.content}
                   for m in history if m.role in ("user", "assistant") and m.content]

        # ── 5. 裁切总结：上下文过长时 AI 总结旧消息 → 写入记忆 → 保留最近 N 条 ──
        history = _summarize_and_trim(messages, history, memory, model)

        messages += history[-MAX_CONTEXT_MESSAGES:]

        # ── 6. 调 AI（带 function calling 循环） ──
        provider = get_ai_provider(model)

        ai_achievements = []  # AI 自主授予的成就
        def _ach_callback(ach_id):
            for ach in ACHIEVEMENTS:
                if ach["id"] == ach_id:
                    result = ach_store.force_unlock(ach)
                    if result:
                        ai_achievements.append(AchievementVO(
                            id=result["id"], name=result["name"],
                            desc=result["desc"], emoji=result["emoji"],
                            tier=result.get("tier", "bronze"),
                        ))
                    return result["name"] if result else "已解锁"
            return "未知成就"

        # 工具映射
        tool_map = build_tool_map(personality, memory, _ach_callback)

        tools_seen = set()
        for _ in range(MAX_TOOL_ROUNDS):
            response = provider.chat(messages, TOOLS, "auto")
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                ai_content = response.get("content", "")
                break

            messages.append({"role": "assistant", "content": response.get("content") or "", "tool_calls": tool_calls})

            for tc in tool_calls:
                fn = tc["function"]
                args = json.loads(fn["arguments"])
                handler = tool_map.get(fn["name"])
                result = handler(**args) if handler else f"未知工具：{fn['name']}"
                # 工具使用统计
                tools_seen.add(fn["name"])
                if fn["name"] == "get_current_time":
                    ach_store.increment_stat("tool_get_current_time")
                elif fn["name"] == "get_silence_hours":
                    ach_store.increment_stat("tool_get_silence_hours")
                elif fn["name"] == "check_memory":
                    ach_store.increment_stat("tool_check_memory")
                elif fn["name"] == "calc":
                    ach_store.increment_stat("tool_calc")
                elif fn["name"] == "translate":
                    ach_store.increment_stat("tool_translate")
                    ach_store.append_stat("translate_directions", args.get("target", ""))
                elif fn["name"] == "set_tone" and args.get("tone") == "safety":
                    ach_store.increment_stat("tone_safety_triggered")
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result
                })
        else:
            # 超过最大循环次数，最后强制要求总结
            messages.append({"role": "user", "content": "请根据已有信息用自然语言回复用户。"})
            final = provider.chat(messages)
            ai_content = final.get("content", "抱歉，我暂时无法回答这个问题。")

        for t in tools_seen:
            ach_store.append_stat("tools_used", t)

        # ── 6.5 强制投入度调整：AI 不调就代码调 ──
        _enforce_engagement(messages, personality, message)
        if personality.engagement < 100:
            _enforce_attention(messages, personality, engagement_before)

        # ── 7. 保存 AI 回复 ──
        if ai_content:
            ai_chat_db.create_message(conversation_id, "assistant", ai_content)
            # 检测 AI 是否引用了记忆，标记召回
            _mark_recalled_from_response(ai_content, message, memory)
        ai_chat_db.touch_conversation(conversation_id)

        # ── 8. 持久化人格状态 ──
        personality.passive_decay()
        personality.save(os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json"))

        # ── 8.5 成就检测 ──
        new_achievements = _check_achievements(user_id, message, personality, memory, conversation_id)
        new_achievements.extend(ai_achievements)

        # ── 9. 返回 ──
        ai_message = ai_chat_db.get_messages_by_conversation(conversation_id)[-1]
        today_count = ai_chat_db.count_user_messages_today(user_id)
        state = AIStateVO(
            tone=personality.tone.value,
            tone_label=_tone_label(personality.tone),
            engagement=personality.engagement,
            attention=personality.attention,
            silence_hours=round(personality.silence_hours, 1),
            memory_count=len(memory),
            messages_today=today_count,
            messages_limit="∞" if is_unlocked else MAX_MESSAGES_PER_DAY,
        )
        return ApiResponse(msg="回复成功", data=ChatReplyVO(
            conversation_id=conversation_id,
            message=to_message_vo(ai_message),
            state=state,
            new_achievements=new_achievements,
        ))
