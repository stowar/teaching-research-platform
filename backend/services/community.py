from backend.db import community_db
from backend.core.exceptions import BusinessException

def create_post_service(post_data, user: dict):
    """
    创建帖子
    :param post_data: PostCreate 模型
    :param user: 当前登录用户（来自 JWT 解析）
    :return: dict
    """
    # 1. 发帖人 = 当前登录用户
    community_db.create_post(post_data, user["id"])

    # 3. 返回
    return {
        "code": 200,
        "msg": "发布成功"
    }

def get_post_list_service(category_id=None, sort='new', keyword=None, page=1, page_size=10):
    """
    获取帖子列表
    :return: dict {code, msg, data: [posts], total}
    """
    # 1. 调 DB 层拿列表数据
    posts = community_db.get_post_list(category_id, sort, keyword, page, page_size)

    # 2. 裁切 content 为摘要（前 100 字）
    for post in posts:
        if post["content"] and len(post["content"]) > 100:
            post["content"] = post["content"][:100] + "..."

    # 3. 返回
    return {
        "code": 200,
        "msg": "查询成功",
        "data": posts
    }

def get_post_detail_service(post_id):
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)
    community_db.increment_view_count(post_id)
    return {
        "code": 200,
        "msg": "查询成功",
        "data": post
    }


def update_post_service(post_id, update_data, user):
    # 1. 查出原帖
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)

    # 2. 校验是不是作者本人
    if post["user_id"] != user["id"]:
        raise BusinessException("只有作者本人才能编辑", code=403)

    # 3. 调 DB 更新
    community_db.update_post(post_id, update_data)

    return {
        "code": 200,
        "msg": "更新成功"
    }


def delete_post_service(post_id, user):
    post = community_db.get_post_by_id(post_id)
    if not post:
        raise BusinessException("帖子不存在", code=404)

    # 作者本人或管理员才能删
    if post["user_id"] != user["id"] and user.get("role") != "admin":
        raise BusinessException("只有作者本人或管理员才能删除", code=403)

    community_db.delete_post(post_id)

    return {
        "code": 200,
        "msg": "删除成功"
    }


# ===================== 分类 =====================

def get_categories_service():
    categories = community_db.get_all_categories()
    return {"code": 200, "msg": "查询成功", "data": categories}


# ===================== 评论 =====================

def get_comments_service(post_id, page=1, page_size=20):
    """获取帖子的评论列表"""
    comments = community_db.get_comments_by_post(post_id, page, page_size)
    return {"code": 200, "msg": "查询成功", "data": comments}


def create_comment_service(post_id, content, parent_id, is_anonymous, user: dict):
    """发表评论"""
    community_db.create_comment(post_id, user["id"], content, parent_id, is_anonymous)
    community_db.update_post_like_count(post_id, delta_comments=1)
    return {"code": 200, "msg": "评论成功"}


def delete_comment_service(comment_id, user: dict):
    """删除评论（作者本人或管理员）"""
    comment = community_db.get_comment_by_id(comment_id)
    if not comment:
        raise BusinessException("评论不存在", code=404)
    if comment["user_id"] != user["id"] and user.get("role") != "admin":
        raise BusinessException("只有作者本人或管理员才能删除", code=403)
    community_db.delete_comment(comment_id)
    return {"code": 200, "msg": "删除成功"}


# ===================== 点赞 =====================

def toggle_like_service(post_id, user: dict):
    """点赞/取消点赞"""
    liked = community_db.toggle_like(post_id, user["id"])
    delta = 1 if liked else -1
    community_db.update_post_like_count(post_id, delta_likes=delta)
    return {"code": 200, "msg": "点赞成功" if liked else "已取消点赞", "liked": liked}


def has_liked_service(post_id, user: dict):
    """检查当前用户是否已点赞"""
    return {"code": 200, "data": {"liked": community_db.has_liked(post_id, user["id"])}}
