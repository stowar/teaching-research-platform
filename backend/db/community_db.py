from backend.db.connection import execute_query, execute_one, execute_update
from datetime import datetime


def get_post_list(category_id=None, sort='new', keyword=None, user_id=None, page=1, page_size=10):
    """
    查询帖子列表篇
    :param category_id: 种类id
    :param sort: 排序方式
    :param keyword: 关键词搜索
    :param user_id: 用户ID（查自己的帖子）
    :param page: 页数
    :param page_size: 一页容纳的尺寸
    :return:
    """
    # 1. 拼 SQL：SELECT posts JOIN users 拿到作者名
    sql = """
        SELECT p.*, u.name AS author_name, c.name AS category_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.status = 1
    """

    params = []

    # 2. 分类筛选
    if category_id:
        sql += " AND p.category_id = %s"
        params.append(category_id)

    # 3. 用户筛选
    if user_id:
        sql += " AND p.user_id = %s"
        params.append(user_id)

    # 4. 关键词搜索
    if keyword:
        sql += " AND (p.title LIKE %s OR p.content LIKE %s)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])

    # 5. 排序
    if sort == 'new':
        sql += " ORDER BY p.create_time DESC"
    elif sort == 'hot':
        sql += " ORDER BY (p.comment_count*3 + p.like_count*2 + p.view_count*0.5) DESC"

    # 6. 分页
    offset = (page - 1) * page_size
    sql += " LIMIT %s OFFSET %s"
    params.append(page_size)
    params.append(offset)

    return execute_query(sql, params)


def get_post_by_id(post_id):
    """根据id获取帖子（含作者名）"""
    sql = """
        SELECT p.*, u.name AS author_name, c.name AS category_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s AND p.status = 1
    """
    return execute_one(sql, (post_id,))


def create_post(post_data, user_id):
    """创建新帖子"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_anonymous = getattr(post_data, 'is_anonymous', 0)
    sql = "INSERT INTO posts (title, content, user_id, category_id, is_anonymous, create_time) VALUES (%s, %s, %s, %s, %s, %s)"
    return execute_update(sql, (post_data.title, post_data.content, user_id, post_data.category_id, is_anonymous, now))


def update_post(post_id, update_data):
    """
    更新帖子信息
    :param post_id: 帖子ID
    :param update_data: dict:更新数据
    :return:
    """
    update_fields = []
    params = []

    if update_data.title is not None:    # ← 用 is not None，避免空字符串被跳过
        update_fields.append("title = %s")
        params.append(update_data.title) # ← 值

    if update_data.content is not None:
        update_fields.append("content = %s")
        params.append(update_data.content)

    if update_data.category_id is not None:
        update_fields.append("category_id = %s")
        params.append(update_data.category_id)

    if not update_fields:
        return 0

    params.append(post_id)
    sql = f"UPDATE posts SET {','.join(update_fields)} WHERE id = %s"

    return execute_update(sql, params)


def delete_post(post_id):
    """删除帖子"""
    sql = "UPDATE posts SET status = 2 WHERE id = %s"
    return execute_update(sql, (post_id,))


def increment_view_count(post_id):
    """增加帖子查看数"""
    sql = "UPDATE posts SET view_count = view_count + 1 WHERE id = %s"
    return execute_update(sql, (post_id,))


def update_post_like_count(post_id, delta_likes=0, delta_comments=0):
    """
    修改帖子点赞数和评论数
    :param post_id: 帖子ID
    :param delta_likes: 增加/减少 的点赞数
    :param delta_comments: 增加/减少 的评论数
    :return:
    """
    sql = "UPDATE posts SET like_count = like_count + %s, comment_count = comment_count + %s WHERE id = %s"
    return execute_update(sql, (delta_likes, delta_comments, post_id))


# ===================== 分类 =====================

def get_all_categories():
    """获取所有分类"""
    sql = "SELECT * FROM categories ORDER BY sort_order ASC"
    return execute_query(sql)


# ===================== 评论 =====================

def get_comments_by_post(post_id, page=1, page_size=20):
    """分页获取帖子的评论列表"""
    offset = (page - 1) * page_size
    sql = """
        SELECT c.*, u.name AS author_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = %s AND c.status = 1
        ORDER BY c.create_time ASC
        LIMIT %s OFFSET %s
    """
    return execute_query(sql, (post_id, page_size, offset))


def create_comment(post_id, user_id, content, parent_id=None, is_anonymous=0):
    """创建评论"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO comments (post_id, user_id, parent_id, content, is_anonymous, create_time) VALUES (%s, %s, %s, %s, %s, %s)"
    return execute_update(sql, (post_id, user_id, parent_id, content, is_anonymous, now))


def delete_comment(comment_id):
    """软删除评论"""
    sql = "UPDATE comments SET status = 0 WHERE id = %s"
    return execute_update(sql, (comment_id,))


def get_comment_by_id(comment_id):
    """根据ID获取单条评论"""
    sql = "SELECT * FROM comments WHERE id = %s AND status = 1"
    return execute_one(sql, (comment_id,))


# ===================== 通知 =====================

def create_notification(user_id, sender_id, notif_type, post_id, comment_id=None, content=''):
    """创建通知"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO notifications (user_id, sender_id, type, post_id, comment_id, content, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    return execute_update(sql, (user_id, sender_id, notif_type, post_id, comment_id, content, now))


def get_notifications(user_id, page=1, page_size=20):
    """获取用户通知列表（含触发者名称）"""
    offset = (page - 1) * page_size
    sql = """
        SELECT n.*, u.name AS sender_name
        FROM notifications n
        JOIN users u ON n.sender_id = u.id
        WHERE n.user_id = %s
        ORDER BY n.create_time DESC
        LIMIT %s OFFSET %s
    """
    return execute_query(sql, (user_id, page_size, offset))


def get_unread_count(user_id):
    """获取未读通知数"""
    sql = "SELECT COUNT(*) AS cnt FROM notifications WHERE user_id = %s AND is_read = 0"
    result = execute_one(sql, (user_id,))
    return result['cnt'] if result else 0


def mark_notification_read(notif_id, user_id):
    """标记单条通知已读"""
    sql = "UPDATE notifications SET is_read = 1 WHERE id = %s AND user_id = %s"
    return execute_update(sql, (notif_id, user_id))


def mark_all_read(user_id):
    """标记所有通知已读"""
    sql = "UPDATE notifications SET is_read = 1 WHERE user_id = %s"
    return execute_update(sql, (user_id,))


def delete_notification(notif_id, user_id):
    """删除通知（只能删自己的）"""
    sql = "DELETE FROM notifications WHERE id = %s AND user_id = %s"
    return execute_update(sql, (notif_id, user_id))


# ===================== 点赞 =====================

def toggle_like(post_id, user_id):
    """给帖子点赞/取消点赞（幂等），返回 True=已赞 False=已取消"""
    sql_check = "SELECT id FROM likes WHERE post_id = %s AND user_id = %s"
    existing = execute_one(sql_check, (post_id, user_id))
    if existing:
        sql_del = "DELETE FROM likes WHERE post_id = %s AND user_id = %s"
        execute_update(sql_del, (post_id, user_id))
        return False
    else:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_add = "INSERT INTO likes (post_id, user_id, create_time) VALUES (%s, %s, %s)"
        execute_update(sql_add, (post_id, user_id, now))
        return True


def has_liked(post_id, user_id):
    """检查用户是否已点赞"""
    sql = "SELECT id FROM likes WHERE post_id = %s AND user_id = %s"
    return execute_one(sql, (post_id, user_id)) is not None