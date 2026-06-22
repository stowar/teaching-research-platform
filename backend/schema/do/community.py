# -*- coding: utf-8 -*-
"""教研社区模块 DO — 数据库表行完整映射"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PostDO(BaseModel):
    """posts 表完整行 + JOIN author_name / category_name"""
    id: int
    user_id: int
    category_id: int
    title: str
    content: str
    view_count: int
    like_count: int
    comment_count: int
    is_pinned: int
    is_essence: int
    is_anonymous: int
    status: int
    create_time: datetime
    update_time: Optional[datetime] = None
    author_name: Optional[str] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class CommentDO(BaseModel):
    """comments 表完整行 + JOIN author_name"""
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    is_anonymous: int
    status: int
    create_time: datetime
    author_name: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationDO(BaseModel):
    """notifications 表完整行 + JOIN sender_name"""
    id: int
    user_id: int
    sender_id: int
    type: str
    post_id: int
    comment_id: Optional[int] = None
    content: str
    is_read: int
    create_time: datetime
    sender_name: Optional[str] = None

    class Config:
        from_attributes = True


class CategoryDO(BaseModel):
    """categories 表完整行"""
    id: int
    name: str
    sort_order: int
    create_time: Optional[datetime] = None

    class Config:
        from_attributes = True
