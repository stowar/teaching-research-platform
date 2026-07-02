# -*- coding: utf-8 -*-
"""AI 聊天室 Request — 前端 → 后端"""
from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """发送消息请求"""
    conversation_id: Optional[int] = Field(None, description="会话ID，为空则自动创建新会话")
    message: str = Field(..., min_length=1, max_length=50000, description="用户消息")
    images: Optional[list] = Field(None, description="base64 图片数组")
    model: Optional[str] = None
    enable_search: bool = Field(True, description="允许 AI 联网搜索")
    enable_deep_think: bool = Field(True, description="允许 AI 深度思考")


class RenameConversation(BaseModel):
    """重命名会话请求"""
    title: str = Field(..., min_length=1, max_length=50)
