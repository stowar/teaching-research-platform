# -*- coding: utf-8 -*-
"""AI 聊天室 API — RESTful 端点"""
from typing import List

import json
import os
import time
from fastapi import APIRouter, Depends, Query

from backend.core.deps import get_ai_chat_service, get_current_user, require_admin
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.ai_chat import ConversationVO, ConversationDetailVO, ChatReplyVO, AIStateVO, AchievementVO
from backend.schema.request.ai_chat import ChatRequest, RenameConversation
from backend.domain.ai_chat import IAIChatService

router = APIRouter(prefix="/ai-chat", tags=["AI聊天室"])


# ===================== 会话管理 =====================

@router.get("/conversations", summary="会话列表", response_model=ApiResponse[List[ConversationVO]])
def get_conversations(
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.get_conversations(current_user.id)


@router.get("/conversations/{conversation_id}", summary="会话详情", response_model=ApiResponse[ConversationDetailVO])
def get_conversation_detail(
    conversation_id: int,
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.get_conversation_detail(conversation_id, current_user.id)


@router.put("/conversations/{conversation_id}/rename", summary="重命名会话", response_model=ApiResponse)
def rename_conversation(
    conversation_id: int,
    data: RenameConversation,
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.rename_conversation(conversation_id, data.title, current_user.id)


@router.delete("/conversations/{conversation_id}", summary="删除会话", response_model=ApiResponse)
def delete_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.delete_conversation(conversation_id, current_user.id)


# ===================== 对话 =====================

@router.post("/chat", summary="发送消息", response_model=ApiResponse[ChatReplyVO])
def chat(
    data: ChatRequest,
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.chat(current_user.id, data.message, data.conversation_id, data.model, current_user.role, (current_user.name or ""), data.images)


@router.get("/state", summary="AI 状态", response_model=ApiResponse[AIStateVO])
def get_state(
    conversation_id: int = Query(None),
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.get_state(current_user.id, conversation_id, current_user.role)


@router.get("/achievements", summary="成就列表", response_model=ApiResponse[List[AchievementVO]])
def get_achievements(
    current_user=Depends(get_current_user),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    return svc.get_achievements(current_user.id)


@router.post("/admin/unlock-user", summary="解锁用户配额", response_model=ApiResponse)
def unlock_user_quota(
    user_id: int = Query(...),
    current_user=Depends(require_admin),
    svc: IAIChatService = Depends(get_ai_chat_service),
):
    override_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "backend", "data", "ai", "quota_override.json"
    )
    os.makedirs(os.path.dirname(override_path), exist_ok=True)
    today = time.strftime("%Y-%m-%d")
    overrides = {}
    try:
        with open(override_path, "r") as f:
            overrides = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    overrides[str(user_id)] = today
    with open(override_path, "w") as f:
        json.dump(overrides, f)
    return ApiResponse(msg=f"已解锁用户 {user_id} 的本日配额")
