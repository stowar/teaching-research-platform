from backend.db.connection import execute_query, execute_one, execute_update
from backend.model.user import UserDO, UserCreate, UserUpdate
from backend.core.security import get_password_hash
from datetime import datetime


def get_user_by_id(user_id: int):
    """根据id获取用户，返回 UserDO"""
    sql = "SELECT * FROM users WHERE id = %s"
    row = execute_one(sql, (user_id,))
    return UserDO.model_validate(row) if row else None


def get_user_by_phone(phone: str):
    """根据手机号获取用户，返回 UserDO"""
    sql = "SELECT * FROM users WHERE phone = %s AND status = 1"
    row = execute_one(sql, (phone,))
    return UserDO.model_validate(row) if row else None


def create_user(user: UserCreate):
    """创建新用户"""
    # 密码加密
    hashed_password = get_password_hash(user.password)
    # 获取时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 默认角色和状态
    role = "user"
    status = 1
    sql = "INSERT INTO users (phone, password, name, school, title, role, status, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    return execute_update(sql, (user.phone, hashed_password, user.name, user.school,user.title, role, status,now))


def update_user_info(user_id: int,user_update: UserUpdate):
    """更新用户信息"""
    update_fields = []
    params = []
    if user_update.name is not None:
        update_fields.append("name = %s")
        params.append(user_update.name)
    if user_update.school is not None:
        update_fields.append("school = %s")
        params.append(user_update.school)
    if user_update.title is not None:
        update_fields.append("title = %s")
        params.append(user_update.title)

    if not update_fields:
        return 0

    params.append(user_id)
    sql = f"UPDATE users SET {','.join(update_fields)} WHERE id = %s"
    return execute_update(sql, params)


def update_user_password(user_id: int, new_password: str):
    """更新用户密码"""
    sql = "UPDATE users SET password = %s WHERE id = %s"
    return execute_update(sql, (new_password, user_id))


def update_user_status(user_id: int, status: int):
    """更新用户状态"""
    sql = "UPDATE users SET status = %s WHERE id = %s"
    return execute_update(sql, (status, user_id))


def get_all_users():
    """获取所有用户，返回 list[UserDO]"""
    rows = execute_query("SELECT * FROM users ORDER BY create_time DESC")
    return [UserDO.model_validate(r) for r in rows]


