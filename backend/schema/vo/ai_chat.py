# -*- coding: utf-8 -*-
"""AI 聊天室 VO — API 输出"""
from typing import List, Optional, Union, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from backend.schema.do.ai_chat import ConversationDO, MessageDO


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


class ConversationVO(BaseModel):
    """会话列表项 VO"""
    id: int
    title: str
    model: str
    message_count: int
    create_time: str
    update_time: str


class MessageVO(BaseModel):
    """消息 VO"""
    id: int = 0
    role: str
    content: str
    timestamp: int   # 前端用毫秒时间戳


class ConversationDetailVO(BaseModel):
    """会话详情 VO（含消息列表）"""
    id: int
    title: str
    model: str
    messages: List["MessageVO"]


class AIStateVO(BaseModel):
    """AI 助手当前状态 VO"""
    tone: str
    tone_label: str
    engagement: int
    attention: int
    silence_hours: float
    memory_count: int
    messages_today: int
    messages_limit: Union[int, str]


class AchievementVO(BaseModel):
    """成就 VO"""
    id: str
    name: str
    desc: str
    emoji: str
    tier: str = "bronze"
    unlock_time: str = ""
    unlocked: bool = False


class ChatReplyVO(BaseModel):
    """AI 回复 VO（非流式）"""
    conversation_id: int
    message: "MessageVO"
    state: Optional["AIStateVO"] = None
    new_achievements: List["AchievementVO"] = []


# ===================== 转换函数 =====================


def to_conversation_vo(c: "ConversationDO", msg_count: int) -> ConversationVO:
    return ConversationVO(
        id=c.id,
        title=c.title,
        model=c.model,
        message_count=msg_count,
        create_time=_fmt(c.create_time),
        update_time=_fmt(c.update_time),
    )


def to_message_vo(m: "MessageDO") -> MessageVO:
    return MessageVO(
        id=m.id,
        role=m.role,
        content=m.content,
        timestamp=int(m.create_time.timestamp() * 1000),
    )
