# -*- coding: utf-8 -*-
"""AI 聊天室 Request — 前端 → 后端"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """发送消息请求"""
    conversation_id: Optional[int] = Field(None, description="会话ID，为空则自动创建新会话")
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息")
    model: Optional[str] = None


class RenameConversation(BaseModel):
    """重命名会话请求"""
    title: str = Field(..., min_length=1, max_length=50)
