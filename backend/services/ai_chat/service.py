# -*- coding: utf-8 -*-
"""AIChatService — 会话管理 + 状态 + 成就 + 对话编排"""
from __future__ import annotations

import base64
import os
from typing import Optional, Tuple

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
from backend.Agent.achievements import AchievementStore, ACHIEVEMENTS
from backend.Agent.preprocessor import PreprocessResult
from backend.Agent.rules import MAX_CONTEXT_MESSAGES, MAX_MESSAGES_PER_DAY, SUMMARIZE_THRESHOLD, DEFAULT_MODEL
from backend.Agent.tools import build_tool_map
from backend.core.config import settings

from .helpers import (
    AI_DATA_DIR, TONE_LABELS, is_unlocked, process_image,
    tone_label as _tone_label, infer_delta,
)
from .pipeline import (
    enforce_silence, summarize_and_trim, resolve_model,
    _make_tool_map,
    phase1_extract, collect_context, phase1_optimize,
    phase2_assemble, phase3_respond,
)
from .achievements import check_achievements


class AIChatService(IAIChatService):

    # ==================== 会话管理 ====================

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
            id=conv.id, title=conv.title, model=conv.model,
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

    # ==================== AI 状态 ====================

    def get_state(self, user_id, conversation_id: int = None, role: str = "user"):
        if conversation_id:
            personality = Personality.load(
                os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json"))
            memory = MemoryStore(conversation_id, AI_DATA_DIR)
        else:
            personality = Personality()
            memory = MemoryStore(0, AI_DATA_DIR)
        today_count = ai_chat_db.count_user_messages_today(user_id)
        limit = "∞" if (role == "admin" or is_unlocked(user_id)) else MAX_MESSAGES_PER_DAY
        return ApiResponse(msg="查询成功", data=AIStateVO(
            tone=personality.tone.value,
            tone_label=_tone_label(personality.tone),
            engagement=personality.engagement,
            attention=personality.attention,
            silence_hours=round(personality.silence_timing / 3600, 1),
            memory_count=len(memory),
            messages_today=today_count,
            messages_limit=limit,
        ))

    # ==================== 成就系统 ====================

    def get_achievements(self, user_id):
        from backend.Agent.achievements import TIER_LABELS, TIER_ORDER, TIER_NAMES
        store = AchievementStore(user_id, AI_DATA_DIR)
        all_unlocked = store.get_all()
        unlocked_map = {item["id"]: item.get("time", "") for item in all_unlocked}
        items = []
        for ach in ACHIEVEMENTS:
            tier = ach.get("tier", "bronze")
            unlocked = ach["id"] in unlocked_map
            items.append({
                "id": ach["id"], "name": ach["name"], "desc": ach["desc"],
                "emoji": ach["emoji"], "tier": tier,
                "tier_label": TIER_LABELS.get(tier, tier),
                "unlock_time": unlocked_map.get(ach["id"], ""),
                "unlocked": unlocked,
            })
        return ApiResponse(msg="查询成功", data={
            "items": items, "tier_order": TIER_ORDER,
            "tier_names": TIER_NAMES, "tier_labels": TIER_LABELS,
        })

    # ═══════════════════════════════════════════════════
    # 对话核心
    # ═══════════════════════════════════════════════════

    def chat(self, user_id, message, conversation_id=None, model=None, role="user", user_name="",
             images=None, documents=None, enable_search=True, enable_deep_think=True):
        unlocked = role == "admin" or is_unlocked(user_id)

        if not self._check_quota(user_id, unlocked):
            return ApiResponse(msg="额度已用完", data=ChatReplyVO(
                conversation_id=conversation_id or 0,
                message=MessageVO(role="assistant", content="今日消息已达上限，请明天再来。", timestamp=0),
            ))

        # 轻量操作用 flash
        conversation_id, message, db_message = self._prepare_message(
            user_id, message, conversation_id, DEFAULT_MODEL, images, documents)

        personality, memory, ach_store, user_state = self._load_conversation_state(
            user_id, conversation_id, message, role, unlocked, db_message)
        engagement_before = personality.engagement

        history = self._load_history(conversation_id, memory, DEFAULT_MODEL)

        # 三阶段管道: AI提取 → 代码收集 → AI优化 → 代码组装 → AI回复
        code_tools = _make_tool_map(personality, memory)
        extraction = phase1_extract(message, history, code_tools)
        final_model = resolve_model(PreprocessResult(
            search_needed=extraction.get("search_needed", False),
            deep_think_needed=extraction.get("deep_think_needed", False),
        ), personality.engagement, model, enable_deep_think)
        context = collect_context(extraction, message, db_message, personality,
                                  memory, ach_store, code_tools)
        optimized = phase1_optimize(message, extraction, context, code_tools)
        prompt = phase2_assemble(optimized, extraction, context, personality, user_state, user_name)
        ai_content, ai_achievements = phase3_respond(
            prompt, history, personality, memory, ach_store, final_model)

        # 后处理
        self._enforce_engagement_check(history, personality, message, engagement_before)
        ai_chat_db.create_message(conversation_id, "assistant", ai_content)
        self._mark_recalled(ai_content, message, memory)
        ai_chat_db.touch_conversation(conversation_id)

        personality.passive_decay()
        personality.save(os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json"))

        new_ach = check_achievements(user_id, message, personality, memory, conversation_id)
        new_ach.extend(ai_achievements)

        return self._build_reply(conversation_id, user_id, personality, unlocked, new_ach)

    # ═══════════════════════════════════════════════════
    # 私有方法
    # ═══════════════════════════════════════════════════

    @staticmethod
    def _check_quota(user_id: int, is_unlocked: bool) -> bool:
        return is_unlocked or ai_chat_db.count_user_messages_today(user_id) < MAX_MESSAGES_PER_DAY

    @staticmethod
    def _prepare_message(user_id: int, message: str, conversation_id: Optional[int],
                         model: str, images: Optional[list],
                         documents: Optional[list] = None) -> Tuple[int, str, str]:
        if conversation_id:
            conv = ai_chat_db.get_conversation_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise BusinessException("会话不存在", code=404)
        else:
            title = (message or "文件对话")[:20] + ("..." if len(message or "") > 20 else "")
            conversation_id = ai_chat_db.create_conversation(user_id, title, model)

        original_message = message  # 保存原文，文档内容只给 AI 看

        # ── 文档解析: Word/PPT 提文字, PDF 逐页转图片 ──
        doc_text = ""
        if documents:
            from backend.utils.file_parser import parse_document
            for doc in documents:
                try:
                    data = base64.b64decode(doc["data"]) if "data" in doc else base64.b64decode(doc.get("base64", ""))
                    text, pdf_images = parse_document(data, doc.get("filename", ""))
                    if text:
                        doc_text += f"\n\n[文档内容: {doc.get('filename', '未知')}]\n{text}"
                    if pdf_images:
                        if images is None:
                            images = []
                        images.extend(pdf_images)
                except Exception:
                    pass
        if doc_text:
            message = doc_text + "\n\n[用户消息]\n" + message if message.strip() else doc_text

        # ── OCR: 图片文字提取 ──
        ocr_text = ""
        if images:
            ocr_parts = []
            for img in images:
                ocr = process_image(img)
                if ocr:
                    ocr_parts.append(ocr)
            if ocr_parts:
                AchievementStore(user_id, AI_DATA_DIR).increment_stat("ocr_used")
                ocr_text = "\n---\n".join(ocr_parts)
                message = f"{message}\n\n[本次上传图片内容]\n{ocr_text}" if message.strip() else f"[本次上传图片内容]\n{ocr_text}"

        # db_message: 原文 + 文件标签（不包含文档内容）
        file_tags = []
        if documents:
            for doc in documents:
                fname = doc.get("filename", "文件")
                ext = fname.rsplit(".", 1)[-1].upper() if "." in fname else ""
                file_tags.append(f"[📄 {ext} {fname}]")
        if file_tags:
            db_message = " ".join(file_tags) + ("\n" + original_message if original_message.strip() else "")
        else:
            db_message = original_message
        typed_text = message[:len(message) - len(ocr_text)] if ocr_text else message
        if len(typed_text) > 5000:
            try:
                provider = get_ai_provider(model or DEFAULT_MODEL)
                resp = provider.chat([{"role": "user", "content": f"提取以下文本的关键信息（200字以内，保留核心数据和结论）：\n{typed_text[:8000]}"}])
                summary = resp.get("content", "").strip()
                if summary:
                    message = f"[以下为用户长文本的AI摘要] {summary}"
                    if ocr_text:
                        message += f"\n\n[图片OCR文字]\n{ocr_text}"
            except Exception:
                pass

        ai_chat_db.create_message(conversation_id, "user", db_message)
        return conversation_id, message, db_message

    @staticmethod
    def _load_conversation_state(user_id: int, conversation_id: int, message: str,
                                  role: str, is_unlocked: bool, raw_message: str = None
                                  ) -> Tuple[Personality, MemoryStore, AchievementStore, dict]:
        personality = Personality.load(
            os.path.join(AI_DATA_DIR, f"conv_{conversation_id}_personality.json"))
        enforce_silence(personality)
        # 用原始输入做关键词匹配，避免 OCR/摘要文本误触发语气切换
        personality.on_user_message(raw_message or message)
        memory = MemoryStore(conversation_id, AI_DATA_DIR)

        ach_store = AchievementStore(user_id, AI_DATA_DIR)
        ach_unlocked = ach_store.get_all()
        ach_unlocked_ids = [item["id"] for item in ach_unlocked]
        ach_names = [a["name"] for a in ACHIEVEMENTS if a["id"] in ach_unlocked_ids]

        today_count = ai_chat_db.count_user_messages_today(user_id)
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
        return personality, memory, ach_store, user_state

    @staticmethod
    def _load_history(conversation_id: int, memory: MemoryStore, model: str) -> list:
        history = ai_chat_db.get_messages_by_conversation(conversation_id)
        history = [{"role": m.role, "content": m.content}
                   for m in history if m.role in ("user", "assistant") and m.content]
        if len(history) > SUMMARIZE_THRESHOLD:
            history = summarize_and_trim(history, memory, model)
        return history

    @staticmethod
    def _enforce_engagement_check(messages: list, personality: Personality,
                                   user_message: str, engagement_before: int):
        called_eng = any(
            tc.get("function", {}).get("name") == "adjust_engagement"
            for msg in messages
            for tc in (msg.get("tool_calls") or []) if isinstance(msg, dict)
        )
        if not called_eng:
            personality.adjust_engagement(infer_delta(user_message))

        if personality.engagement < 100:
            called_att = any(
                tc.get("function", {}).get("name") == "adjust_attention"
                for msg in messages
                for tc in (msg.get("tool_calls") or []) if isinstance(msg, dict)
            )
            if not called_att:
                delta = 5 if personality.engagement > engagement_before else -5
                personality.adjust_attention(delta)

    @staticmethod
    def _mark_recalled(ai_content: str, user_message: str, memory: MemoryStore):
        if "【根据你之前的信息】" not in ai_content and "根据你之前的" not in ai_content:
            return
        keywords = ["研究方向", "偏好", "课程", "教学", "学生", "班级", "公开课", "教案",
                    "写作", "听说", "阅读", "词汇", "任务驱动", "小组", "考试", "教研"]
        for kw in keywords:
            if kw in user_message or kw in ai_content:
                memory.mark_recalled(kw)

    @staticmethod
    def _build_reply(conversation_id: int, user_id: int, personality: Personality,
                     is_unlocked: bool, new_achievements: list) -> ApiResponse:
        ai_message = ai_chat_db.get_messages_by_conversation(conversation_id)[-1]
        today_count = ai_chat_db.count_user_messages_today(user_id)
        state = AIStateVO(
            tone=personality.tone.value,
            tone_label=_tone_label(personality.tone),
            engagement=personality.engagement,
            attention=personality.attention,
            silence_hours=round(personality.silence_timing / 3600, 1),
            memory_count=0,
            messages_today=today_count,
            messages_limit="∞" if is_unlocked else MAX_MESSAGES_PER_DAY,
        )
        return ApiResponse(msg="回复成功", data=ChatReplyVO(
            conversation_id=conversation_id,
            message=to_message_vo(ai_message),
            state=state,
            new_achievements=new_achievements,
        ))
