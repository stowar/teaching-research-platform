from __future__ import annotations

from backend.db import community_db
from backend.core.exceptions import BusinessException
from backend.core.vo.common import ApiResponse
from backend.core.vo.community import (
    PostVO, PostListVO, CommentVO, NotificationVO, CategoryVO, LikedVO, NotificationListVO,
    to_post_vo, to_comment_vo, to_notification_vo, to_category_vo,
)


def create_post_service(post_data, user) -> ApiResponse:
    """创建帖子"""
    community_db.create_post(post_data, user.id)
    return ApiResponse(msg="发布成功")


def get_post_list_service(category_id=None, sort='new', keyword=None, user_id=None, page=1, page_size=10) -> ApiResponse[PostListVO]:
    """获取帖子列表 — 内容截取前100字为摘要，含总数"""
    posts = community_db.get_post_list(category_id, sort, keyword, user_id, page, page_size)
    total = community_db.count_posts(category_id, keyword, user_id)
    vos = []
    for p in posts:
        content = p.content
        if content and len(content) > 100:
            content = content[:100] + "..."
        vo = to_post_vo(p)
        vo.content = content
        vos.append(vo)
    return ApiResponse(msg="查询成功", data=PostListVO(items=vos, total=total))


def get_post_detail_service(post_id) -> ApiResponse[PostVO]:
    """获取帖子详情"""
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)
    community_db.increment_view_count(post_id)
    return ApiResponse(msg="查询成功", data=to_post_vo(post))


def update_post_service(post_id, update_data, user) -> ApiResponse:
    """编辑帖子"""
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)
    if post.user_id != user.id:
        raise BusinessException("只有作者本人才能编辑", code=403)
    community_db.update_post(post_id, update_data)
    return ApiResponse(msg="更新成功")


def delete_post_service(post_id, user) -> ApiResponse:
    """删除帖子"""
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)
    if post.user_id != user.id and user.role != "admin":
        raise BusinessException("只有作者本人或管理员才能删除", code=403)
    community_db.delete_post(post_id)
    return ApiResponse(msg="删除成功")


# ===================== 分类 =====================

def get_categories_service() -> ApiResponse[list[CategoryVO]]:
    """获取分类列表"""
    categories = community_db.get_all_categories()
    return ApiResponse(msg="查询成功", data=[to_category_vo(c) for c in categories])


# ===================== 评论 =====================

def get_comments_service(post_id, page=1, page_size=20) -> ApiResponse[list[CommentVO]]:
    """获取帖子的评论列表"""
    comments = community_db.get_comments_by_post(post_id, page, page_size)
    return ApiResponse(msg="查询成功", data=[to_comment_vo(c) for c in comments])


def create_comment_service(post_id, content, parent_id, is_anonymous, user) -> ApiResponse:
    """发表评论"""
    community_db.create_comment(post_id, user.id, content, parent_id, is_anonymous)
    community_db.update_post_like_count(post_id, delta_comments=1)
    post = community_db.get_post_by_id(post_id)
    if post and post.user_id != user.id:
        community_db.create_notification(
            post.user_id, user.id, 'comment', post_id,
            content=f'{user.name or "有人"} 评论了你的帖子《{post.title}》',
        )
    return ApiResponse(msg="评论成功")


def delete_comment_service(comment_id, user) -> ApiResponse:
    """删除评论（作者本人或管理员）"""
    comment = community_db.get_comment_by_id(comment_id)
    if not comment:
        raise BusinessException("评论不存在", code=404)
    if comment.user_id != user.id and user.role != "admin":
        raise BusinessException("只有作者本人或管理员才能删除", code=403)
    community_db.delete_comment(comment_id)
    return ApiResponse(msg="删除成功")


# ===================== 点赞 =====================

def toggle_like_service(post_id, user) -> ApiResponse[LikedVO]:
    """点赞/取消点赞"""
    liked = community_db.toggle_like(post_id, user.id)
    delta = 1 if liked else -1
    community_db.update_post_like_count(post_id, delta_likes=delta)
    if liked:
        post = community_db.get_post_by_id(post_id)
        if post and post.user_id != user.id:
            community_db.create_notification(
                post.user_id, user.id, 'like', post_id,
                content=f'{user.name or "有人"} 赞了你的帖子《{post.title}》',
            )
    return ApiResponse(
        msg="点赞成功" if liked else "已取消点赞",
        data=LikedVO(liked=liked),
    )


def has_liked_service(post_id, user) -> ApiResponse[LikedVO]:
    """检查当前用户是否已点赞"""
    return ApiResponse(data=LikedVO(liked=community_db.has_liked(post_id, user.id)))


# ===================== 通知 =====================

def get_notifications_service(user, page=1, page_size=20) -> ApiResponse[NotificationListVO]:
    """获取通知列表 + 未读数"""
    notifs = community_db.get_notifications(user.id, page, page_size)
    unread = community_db.get_unread_count(user.id)
    return ApiResponse(
        data=NotificationListVO(
            items=[to_notification_vo(n) for n in notifs],
            unread=unread,
        ),
    )


def mark_read_service(notif_id, user) -> ApiResponse:
    """标记单条已读"""
    community_db.mark_notification_read(notif_id, user.id)
    return ApiResponse(msg="已标记已读")


def mark_all_read_service(user) -> ApiResponse:
    """标记全部已读"""
    community_db.mark_all_read(user.id)
    return ApiResponse(msg="全部已读")


def delete_notification_service(notif_id, user) -> ApiResponse:
    """删除通知（只能删自己的）"""
    community_db.delete_notification(notif_id, user.id)
    return ApiResponse(msg="已删除")
