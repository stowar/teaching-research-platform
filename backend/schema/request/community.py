# -*- coding: utf-8 -*-
"""教研社区模块 Request — 前端 → 后端"""

from typing import Optional
from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    """创建帖子请求"""
    title: str = Field(..., min_length=1, max_length=200, description="帖子标题")
    content: str = Field(..., min_length=1, description="帖子内容")
    category_id: int = Field(..., description="分类ID")
    is_anonymous: int = Field(0, description="是否匿名：1是 0否")


class PostUpdate(BaseModel):
    """编辑帖子请求（只传你想改的字段）"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="帖子标题")
    content: Optional[str] = Field(None, min_length=1, description="帖子内容")
    category_id: Optional[int] = Field(None, description="分类ID")


class CommentCreate(BaseModel):
    """创建评论请求"""
    content: str = Field(..., min_length=1, description="评论内容")
    parent_id: Optional[int] = Field(None, description="回复的评论ID，NULL表示直接回复帖子")
    is_anonymous: int = Field(0, description="是否匿名：1是 0否")
