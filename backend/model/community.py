from pydantic import Field,BaseModel
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    """创建帖子请求"""
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题")
    content: str = Field(..., min_length=1, description="帖子内容")
    category_id: int = Field(..., description="分类ID")


class PostUpdate(BaseModel):
    """编辑帖子请求（只传你想改的字段）"""
    # 填 3 个 Optional 字段
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="帖子标题")
    content: Optional[str] = Field(None, min_length=1, description="帖子内容")
    category_id: Optional[int] = Field(None, description="分类ID")


class PostResponse(BaseModel):
    """帖子响应（返回给前端）"""
    id: int
    user_id: int
    author_name: Optional[str] = None   # 来自 JOIN
    category_id: int
    title: str
    content: str
    view_count: int
    like_count: int
    comment_count: int
    is_pinned: int
    is_essence: int
    status: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, description="评论内容")
    parent_id: Optional[int] = Field(None, description="回复的评论ID，NULL表示直接回复帖子")

