# -*- coding: utf-8 -*-
"""教研社区领域接口 — API 层只能依赖此接口，不感知具体实现"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from backend.schema.vo.common import ApiResponse
from backend.schema.vo.community import (
    PostVO, PostListVO, CommentVO, NotificationListVO, CategoryVO, LikedVO,
)
from backend.schema.request.community import PostCreate, PostUpdate, CommentCreate


class ICommunityService(ABC):
    """教研社区服务接口 — 所有方法必须有对应实现"""

    # ===================== 帖子 =====================

    @abstractmethod
    def create_post_service(self, post_data: PostCreate, user) -> ApiResponse:
        """创建帖子"""
        ...

    @abstractmethod
    def get_post_list_service(self, category_id=None, sort='new', keyword=None,
                              user_id=None, page=1, page_size=10) -> ApiResponse[PostListVO]:
        """获取帖子列表"""
        ...

    @abstractmethod
    def get_post_detail_service(self, post_id: int) -> ApiResponse[PostVO]:
        """获取帖子详情"""
        ...

    @abstractmethod
    def update_post_service(self, post_id: int, post_data: PostUpdate, user) -> ApiResponse:
        """编辑帖子（仅作者本人）"""
        ...

    @abstractmethod
    def delete_post_service(self, post_id: int, user) -> ApiResponse:
        """删除帖子（作者本人或管理员）"""
        ...

    # ===================== 分类 =====================

    @abstractmethod
    def get_categories_service(self) -> ApiResponse[List[CategoryVO]]:
        """获取分类列表"""
        ...

    # ===================== 评论 =====================

    @abstractmethod
    def get_comments_service(self, post_id: int, page=1, page_size=20) -> ApiResponse[List[CommentVO]]:
        """获取评论列表"""
        ...

    @abstractmethod
    def create_comment_service(self, post_id: int, content: str, parent_id: Optional[int],
                               is_anonymous: bool, user) -> ApiResponse:
        """发表评论"""
        ...

    @abstractmethod
    def delete_comment_service(self, comment_id: int, user) -> ApiResponse:
        """删除评论（作者本人或管理员）"""
        ...

    # ===================== 点赞 =====================

    @abstractmethod
    def toggle_like_service(self, post_id: int, user) -> ApiResponse[LikedVO]:
        """点赞/取消点赞"""
        ...

    @abstractmethod
    def has_liked_service(self, post_id: int, user) -> ApiResponse[LikedVO]:
        """查询点赞状态"""
        ...

    # ===================== 通知 =====================

    @abstractmethod
    def get_notifications_service(self, user, page=1, page_size=20) -> ApiResponse[NotificationListVO]:
        """获取通知列表"""
        ...

    @abstractmethod
    def mark_read_service(self, notif_id: int, user) -> ApiResponse:
        """标记单条已读"""
        ...

    @abstractmethod
    def mark_all_read_service(self, user) -> ApiResponse:
        """标记全部已读"""
        ...

    @abstractmethod
    def delete_notification_service(self, notif_id: int, user) -> ApiResponse:
        """删除通知"""
        ...
