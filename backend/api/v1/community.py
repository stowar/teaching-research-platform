# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from backend.core.deps import get_community_service, get_current_user
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.community import (
    PostVO, PostListVO, CommentVO, NotificationListVO, CategoryVO, LikedVO,
)
from backend.domain.community import ICommunityService
from backend.schema.request.community import PostCreate, PostUpdate, CommentCreate

router = APIRouter(prefix="/community", tags=["教研社区"])


# ===================== 帖子 =====================

@router.get("/posts", summary="帖子列表", response_model=ApiResponse[PostListVO])
def get_post_list(
    category_id: int = Query(None),
    sort: str = Query('new'),
    keyword: str = Query(None),
    user_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.get_post_list_service(category_id, sort, keyword, user_id, page, page_size)


@router.get("/posts/{post_id}", summary="帖子详情", response_model=ApiResponse[PostVO])
def get_post_detail(
    post_id: int,
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.get_post_detail_service(post_id)


@router.post("/posts", summary="发布帖子", response_model=ApiResponse)
def create_post(
    post_data: PostCreate,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.create_post_service(post_data, current_user)


@router.put("/posts/{post_id}", summary="编辑帖子", response_model=ApiResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.update_post_service(post_id, post_data, current_user)


@router.delete("/posts/{post_id}", summary="删除帖子", response_model=ApiResponse)
def delete_post(
    post_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.delete_post_service(post_id, current_user)


# ===================== 分类 =====================

@router.get("/categories", summary="分类列表", response_model=ApiResponse[List[CategoryVO]])
def get_categories(
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.get_categories_service()


# ===================== 评论 =====================

@router.get("/posts/{post_id}/comments", summary="评论列表", response_model=ApiResponse[List[CommentVO]])
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.get_comments_service(post_id, page, page_size)


@router.post("/posts/{post_id}/comments", summary="发表评论", response_model=ApiResponse)
def create_comment(
    post_id: int,
    data: CommentCreate,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.create_comment_service(post_id, data.content, data.parent_id, data.is_anonymous, current_user)


@router.delete("/comments/{comment_id}", summary="删除评论", response_model=ApiResponse)
def delete_comment(
    comment_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.delete_comment_service(comment_id, current_user)


# ===================== 点赞 =====================

@router.post("/posts/{post_id}/like", summary="点赞/取消点赞", response_model=ApiResponse[LikedVO])
def toggle_like(
    post_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.toggle_like_service(post_id, current_user)


@router.get("/posts/{post_id}/like", summary="查询点赞状态", response_model=ApiResponse[LikedVO])
def has_liked(
    post_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.has_liked_service(post_id, current_user)


# ===================== 通知 =====================

@router.get("/notifications", summary="通知列表", response_model=ApiResponse[NotificationListVO])
def get_notifications(
    page: int = Query(1, ge=1),
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.get_notifications_service(current_user, page)


@router.put("/notifications/{notif_id}/read", summary="标记已读", response_model=ApiResponse)
def mark_read(
    notif_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.mark_read_service(notif_id, current_user)


@router.put("/notifications/read-all", summary="全部已读", response_model=ApiResponse)
def mark_all_read(
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.mark_all_read_service(current_user)


@router.delete("/notifications/{notif_id}", summary="删除通知", response_model=ApiResponse)
def delete_notification(
    notif_id: int,
    current_user=Depends(get_current_user),
    svc: ICommunityService = Depends(get_community_service),
):
    return svc.delete_notification_service(notif_id, current_user)
