# -*- coding: utf-8 -*-
"""教研社区模块 VO — 仅 API / Service 层使用"""

from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from backend.schema.do.community import PostDO, CommentDO, NotificationDO, CategoryDO


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


class PostVO(BaseModel):
    """帖子 VO"""
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
    create_time: str
    update_time: str
    author_name: Optional[str] = None
    category_name: Optional[str] = None


class CommentVO(BaseModel):
    """评论 VO"""
    id: int
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    content: str
    is_anonymous: int
    create_time: str
    author_name: Optional[str] = None


class NotificationVO(BaseModel):
    """通知 VO"""
    id: int
    type: str
    post_id: int
    comment_id: Optional[int] = None
    content: str
    is_read: int
    create_time: str
    sender_name: Optional[str] = None


class CategoryVO(BaseModel):
    """分类 VO"""
    id: int
    name: str
    sort_order: int


class LikedVO(BaseModel):
    """点赞状态 VO"""
    liked: bool


class PostListVO(BaseModel):
    """帖子列表 VO（含分页信息）"""
    items: List["PostVO"]
    total: int


class NotificationListVO(BaseModel):
    """通知列表 + 未读数 VO"""
    items: List["NotificationVO"]
    unread: int


def to_post_vo(p: "PostDO") -> PostVO:
    return PostVO(
        id=p.id,
        user_id=p.user_id,
        category_id=p.category_id,
        title=p.title,
        content=p.content,
        view_count=p.view_count,
        like_count=p.like_count,
        comment_count=p.comment_count,
        is_pinned=p.is_pinned,
        is_essence=p.is_essence,
        is_anonymous=p.is_anonymous,
        create_time=_fmt(p.create_time),
        update_time=_fmt(p.update_time),
        author_name=p.author_name,
        category_name=p.category_name,
    )


def to_comment_vo(c: "CommentDO") -> CommentVO:
    return CommentVO(
        id=c.id,
        post_id=c.post_id,
        user_id=c.user_id,
        parent_id=c.parent_id,
        content=c.content,
        is_anonymous=c.is_anonymous,
        create_time=_fmt(c.create_time),
        author_name=c.author_name,
    )


def to_notification_vo(n: "NotificationDO") -> NotificationVO:
    return NotificationVO(
        id=n.id,
        type=n.type,
        post_id=n.post_id,
        comment_id=n.comment_id,
        content=n.content,
        is_read=n.is_read,
        create_time=_fmt(n.create_time),
        sender_name=n.sender_name,
    )


def to_category_vo(c: "CategoryDO") -> CategoryVO:
    return CategoryVO(
        id=c.id,
        name=c.name,
        sort_order=c.sort_order,
    )
