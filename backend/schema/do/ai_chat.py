# -*- coding: utf-8 -*-
"""AI 聊天室 DO — 数据库行完整映射"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ConversationDO(BaseModel):
    """conversations 表完整行 + JOIN msg_count"""
    id: int
    user_id: int
    title: str
    model: str
    status: int
    create_time: datetime
    update_time: Optional[datetime] = None
    msg_count: int = 0   # 来自 JOIN 子查询，非数据库字段

    class Config:
        from_attributes = True


class MessageDO(BaseModel):
    """messages 表完整行"""
    id: int
    conversation_id: int
    role: str
    content: str
    create_time: datetime

    class Config:
        from_attributes = True
