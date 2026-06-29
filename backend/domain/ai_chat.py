# -*- coding: utf-8 -*-
"""AI 聊天室领域接口 — API 层只依赖此接口"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from backend.schema.vo.common import ApiResponse
from backend.schema.vo.ai_chat import ConversationVO, ConversationDetailVO, ChatReplyVO, AIStateVO


class IAIChatService(ABC):
    """AI 聊天室服务接口"""

    # ===================== 会话管理 =====================

    @abstractmethod
    def get_conversations(self, user_id: int) -> ApiResponse[List[ConversationVO]]:
        """获取用户的所有会话列表"""
        ...

    @abstractmethod
    def get_conversation_detail(self, conversation_id: int, user_id: int) -> ApiResponse[ConversationDetailVO]:
        """获取单个会话详情（含历史消息）"""
        ...

    @abstractmethod
    def rename_conversation(self, conversation_id: int, title: str, user_id: int) -> ApiResponse:
        """重命名会话"""
        ...

    @abstractmethod
    def delete_conversation(self, conversation_id: int, user_id: int) -> ApiResponse:
        """删除会话（级联删除消息）"""
        ...

    # ===================== 对话 =====================

    @abstractmethod
    def chat(self, user_id: int, message: str, conversation_id: int = None, model: str = None, role: str = "user") -> ApiResponse[ChatReplyVO]:
        """发送消息并获取 AI 回复"""
        ...

    @abstractmethod
    def get_state(self, user_id: int, conversation_id: int = None) -> ApiResponse[AIStateVO]:
        """获取 AI 当前状态（指定会话则返回该会话人格）"""
        ...
