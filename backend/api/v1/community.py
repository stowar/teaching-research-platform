from fastapi import APIRouter, Depends, Query, HTTPException, Body
from backend.core.deps import get_current_user, require_admin
from backend.core.exceptions import BusinessException
from backend.services import community as community_service
from backend.model.community import PostCreate, PostUpdate, CommentCreate

router = APIRouter(prefix="/community", tags=["教研社区"])


# 1. 帖子列表
@router.get("/posts", summary="帖子列表")
def get_post_list(
    category_id: int = Query(None),
    sort: str = Query('new'),
    keyword: str = Query(None),
    user_id: int = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    """分页查询帖子列表"""
    return community_service.get_post_list_service(category_id, sort, keyword, user_id, page, page_size)


# 2. 帖子详情
@router.get("/posts/{post_id}", summary="帖子详情")
def get_post_detail(post_id: int):
    try:
        return community_service.get_post_detail_service(post_id)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


# 3. 发布帖子
@router.post("/posts", summary="发布帖子")   # 需要登录
def create_post(post_data: PostCreate, current_user = Depends(get_current_user)):
    try:
        return community_service.create_post_service(post_data, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


# 4. 编辑帖子
@router.put("/posts/{post_id}", summary="编辑帖子")   # 需要登录 + 作者本人
def update_post(post_id: int, post_data: PostUpdate, current_user = Depends(get_current_user)):
    try:
        return community_service.update_post_service(post_id, post_data, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


# 5. 删除帖子
@router.delete("/posts/{post_id}", summary="删除帖子")   # 需要登录 + 作者/管理员
def delete_post(post_id: int, current_user = Depends(get_current_user)):
    try:
        return community_service.delete_post_service(post_id, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


# ===================== 分类 =====================

@router.get("/categories", summary="分类列表")
def get_categories():
    return community_service.get_categories_service()


# ===================== 评论 =====================

@router.get("/posts/{post_id}/comments", summary="评论列表")
def get_comments(post_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50)):
    return community_service.get_comments_service(post_id, page, page_size)


@router.post("/posts/{post_id}/comments", summary="发表评论")
def create_comment(post_id: int, data: CommentCreate, current_user = Depends(get_current_user)):
    try:
        return community_service.create_comment_service(post_id, data.content, data.parent_id, data.is_anonymous, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/comments/{comment_id}", summary="删除评论")
def delete_comment(comment_id: int, current_user = Depends(get_current_user)):
    try:
        return community_service.delete_comment_service(comment_id, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


# ===================== 点赞 =====================

@router.post("/posts/{post_id}/like", summary="点赞/取消点赞")
def toggle_like(post_id: int, current_user = Depends(get_current_user)):
    try:
        return community_service.toggle_like_service(post_id, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/posts/{post_id}/like", summary="查询点赞状态")
def has_liked(post_id: int, current_user = Depends(get_current_user)):
    return community_service.has_liked_service(post_id, current_user)


# ===================== 通知 =====================

@router.get("/notifications", summary="通知列表")
def get_notifications(page: int = Query(1, ge=1), current_user = Depends(get_current_user)):
    return community_service.get_notifications_service(current_user, page)


@router.put("/notifications/{notif_id}/read", summary="标记已读")
def mark_read(notif_id: int, current_user = Depends(get_current_user)):
    return community_service.mark_read_service(notif_id, current_user)


@router.put("/notifications/read-all", summary="全部已读")
def mark_all_read(current_user = Depends(get_current_user)):
    return community_service.mark_all_read_service(current_user)


@router.delete("/notifications/{notif_id}", summary="删除通知")
def delete_notification(notif_id: int, current_user = Depends(get_current_user)):
    return community_service.delete_notification_service(notif_id, current_user)
