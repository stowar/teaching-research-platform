# -*- coding: utf-8 -*-
"""AI 聊天室服务 — 对话逻辑 + 状态机 + 记忆系统"""
import json
import os

from backend.domain.ai_chat import IAIChatService
from backend.db import ai_chat_db
from backend.core.exceptions import BusinessException
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.ai_chat import (
    ConversationVO, ConversationDetailVO, MessageVO, ChatReplyVO,
    to_conversation_vo, to_message_vo,
)
from backend.Agent.provider import get_ai_provider
from backend.Agent.personality import Personality
from backend.Agent.tools import TOOLS, MemoryStore, execute_tool
from backend.core.config import settings

# 记忆文件存储目录
AI_DATA_DIR = os.path.join(settings.BASE_DIR, "backend", "data", "ai")


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

        # ── 4. 构建 system prompt ──
        system_prompt = _build_system_prompt(personality, memory)

        # ── 5. 构建消息上下文 ──
        messages = [{"role": "system", "content": system_prompt}]
        history = ai_chat_db.get_messages_by_conversation(conversation_id)
        # 只取最近 30 条作为上下文窗口
        for m in history[-30:]:
            messages.append({"role": m.role, "content": m.content})

        # ── 6. 调 AI（带 function calling 循环） ──
        provider = get_ai_provider(model)
        max_tool_rounds = 3

        for _ in range(max_tool_rounds):
            response = provider.chat(messages, TOOLS, "auto")
            tool_calls = response.get("tool_calls", [])

            if not tool_calls:
                # AI 不需要调工具，直接返回文本
                ai_content = response.get("content", "")
                break

            # AI 调用了工具
            messages.append({"role": "assistant", "content": response.get("content") or "", "tool_calls": tool_calls})

            for tc in tool_calls:
                fn = tc["function"]
                args = json.loads(fn["arguments"])
                result = execute_tool(fn["name"], args, personality, memory)
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
        ai_chat_db.create_message(conversation_id, "assistant", ai_content)
        ai_chat_db.touch_conversation(conversation_id)

        # ── 8. 持久化人格状态 ──
        personality.passive_decay()
        personality.save(os.path.join(AI_DATA_DIR, f"user_{user_id}_personality.json"))

        # ── 9. 返回 ──
        ai_message = ai_chat_db.get_messages_by_conversation(conversation_id)[-1]
        return ApiResponse(msg="回复成功", data=ChatReplyVO(
            conversation_id=conversation_id,
            message=to_message_vo(ai_message),
        ))


def _build_system_prompt(personality: Personality, memory: MemoryStore) -> str:
    """构建 AI 教研助手的 system prompt"""
    tone_desc = personality.get_tone_prompt()
    memories = memory.get_recent_context(10)
    status = personality.get_status()

    prompt = f"""你是 AI 教研助手，专为职业院校英语教师打造。

## 你的职责
- 协助英语教学设计、课堂活动策划、课程思政融合
- 分析教学评价、推荐教研资源、解答教学困惑
- 为教师提供专业、温暖、有针对性的建议

## 当前状态
{status}

## 语气指导
{tone_desc}

## 记忆
{memories if memories else "还不了解这位教师，多问多记。"}

## 交互规则
1. 结合用户的学校类型（职业院校）、学生特点（英语基础偏弱）给实际建议，不空谈理论
2. 如果用户提到之前的经历或偏好，用 remember 工具记下来
3. 如果问题涉及用户之前说过的事，先用 recall 查询
4. 根据对话氛围用 set_tone 调整语气——教师沮丧时多鼓励，深入研讨时变专业
5. 用 markdown 格式化长回答，分点、加粗重点
6. 不要编造你没记住的信息
7. 回复用中文"""
    return prompt
