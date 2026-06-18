from pydantic import Field, BaseModel
from typing import Optional
from datetime import datetime


# ======================
# 0. DO：数据库表行完整映射（仅供 DB / Service 层使用，API 层禁入）
# ======================

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


# ======================
# 1. 请求模型（API 输入）
# ======================

class PostCreate(BaseModel):
    """创建帖子请求"""
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题")
    content: str = Field(..., min_length=1, description="帖子内容")
    category_id: int = Field(..., description="分类ID")
    is_anonymous: int = Field(0, description="是否匿名：1是 0否")


class PostUpdate(BaseModel):
    """编辑帖子请求（只传你想改的字段）"""
    # 填 3 个 Optional 字段
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="帖子标题")
    content: Optional[str] = Field(None, min_length=1, description="帖子内容")
    category_id: Optional[int] = Field(None, description="分类ID")


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, description="评论内容")
    parent_id: Optional[int] = Field(None, description="回复的评论ID，NULL表示直接回复帖子")
    is_anonymous: int = Field(0, description="是否匿名：1是 0否")

