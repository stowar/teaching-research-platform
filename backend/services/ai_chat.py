# -*- coding: utf-8 -*-
"""AI 聊天室服务 — 对话逻辑 + 状态机 + 记忆系统"""
import json
import os

from backend.domain.ai_chat import IAIChatService
from backend.db import ai_chat_db
from backend.core.exceptions import BusinessException
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.ai_chat import (
    ConversationVO, ConversationDetailVO, MessageVO, ChatReplyVO, AIStateVO,
    to_conversation_vo, to_message_vo,
)
from backend.Agent.provider import get_ai_provider
from backend.Agent.personality import Personality
from backend.Agent.tools import TOOLS, MemoryStore, build_tool_map
from backend.Agent.rules import build_system_prompt, MAX_CONTEXT_MESSAGES, MAX_TOOL_ROUNDS, MAX_MESSAGES_PER_DAY, SUMMARIZE_THRESHOLD, KEEP_LAST
from backend.core.config import settings

# 记忆文件存储目录
AI_DATA_DIR = os.path.join(settings.BASE_DIR, "backend", "data", "ai")

TONE_LABELS = {
    "professional": "专业模式",
    "casual": "轻松模式",
    "encouraging": "鼓励模式",
    "analytical": "分析模式",
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


def _tone_label(tone):
    return TONE_LABELS.get(tone.value if hasattr(tone, 'value') else tone, "未知")


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

    # ===================== 对话核心逻辑 =====================

    def chat(self, user_id, message, conversation_id=None, model="deepseek-chat"):
        # ── 0. 每日配额 ──
        today_count = ai_chat_db.count_user_messages_today(user_id)
        if today_count >= MAX_MESSAGES_PER_DAY:
            raise BusinessException(f"今日消息已达上限（{MAX_MESSAGES_PER_DAY}条），请明天再来")

        # ── 1. 会话管理 ──
        if conversation_id:
            conv = ai_chat_db.get_conversation_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise BusinessException("会话不存在", code=404)
        else:
            # 自动创建新会话，用消息前 20 字做标题
            title = message[:20] + ("..." if len(message) > 20 else "")
            conversation_id = ai_chat_db.create_conversation(user_id, title, model)

        # ── 2. 保存用户消息 ──
        ai_chat_db.create_message(conversation_id, "user", message)

        # ── 3. 加载人格和记忆 ──
        personality = Personality.load(
            os.path.join(AI_DATA_DIR, f"user_{user_id}_personality.json")
        )
        personality.on_user_message(message)
        memory = MemoryStore(user_id, AI_DATA_DIR)

        # ── 4. 构建消息上下文 ──
        system_prompt = build_system_prompt(personality, memory)
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

        tool_map = build_tool_map(personality, memory)

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

        # ── 7. 保存 AI 回复 ──
        if ai_content:
            ai_chat_db.create_message(conversation_id, "assistant", ai_content)
        ai_chat_db.touch_conversation(conversation_id)

        # ── 8. 持久化人格状态 ──
        personality.passive_decay()
        personality.save(os.path.join(AI_DATA_DIR, f"user_{user_id}_personality.json"))

        # ── 9. 返回 ──
        ai_message = ai_chat_db.get_messages_by_conversation(conversation_id)[-1]
        today_count = ai_chat_db.count_user_messages_today(user_id)
        state = AIStateVO(
            tone=personality.tone.value,
            tone_label=_tone_label(personality.tone),
            engagement=personality.engagement,
            attention=personality.attention,
            silence_hours=round(personality.silence_hours, 1),
            memory_count=len(memory._load()),
            messages_today=today_count,
            messages_limit=MAX_MESSAGES_PER_DAY,
        )
        return ApiResponse(msg="回复成功", data=ChatReplyVO(
            conversation_id=conversation_id,
            message=to_message_vo(ai_message),
            state=state,
        ))
