from backend.utils.logger import logger
from backend.db.connection import (get_db_connection, execute_one, execute_query, execute_update)
from datetime import datetime
from passlib.context import CryptContext

# 配置加密上下文（直接移入引擎，统一管理）
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==========================
# 🔥 教研平台核心类引擎
# 整合：持久化 + 日志 + 全部用户业务CRUD
# ==========================
class ResearchPlatformEngine:
    def __init__(self):
        # 三大基础能力
        self.logger = logger              # 日志引擎
        self.get_conn = get_db_connection # 持久化引擎
        self.pwd_context = pwd_context    # 密码加密

    # ==========================
    # 👇 你所有的用户操作，全部封装在这里
    # ==========================

    def get_user_by_id(self, user_id: int):
        """根据id获取用户"""
        sql = "SELECT * FROM users WHERE id = %s"
        result = execute_one(sql, (user_id,))
        self.logger.info(f"查询用户ID：{user_id}")
        return result

    def get_user_by_phone(self, phone: str):
        """根据手机号获取用户"""
        sql = "SELECT * FROM users WHERE phone = %s AND status = 1"
        result = execute_one(sql, (phone,))
        self.logger.info(f"查询手机号：{phone}")
        return result

    def create_user(self, user):
        """创建新用户"""
        hashed_password = self.pwd_context.hash(user.password)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        role = "user"
        status = 1
        sql = "INSERT INTO users (phone, password, name, school, title, role, status, create_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        result = execute_update(sql, (
            user.phone, hashed_password, user.name, user.school,
            user.title, role, status, now
        ))
        self.logger.info(f"创建新用户：{user.phone}")
        return result

    def update_user_info(self, user_id: int, user_update):
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
        result = execute_update(sql, params)
        self.logger.info(f"更新用户信息 ID：{user_id}")
        return result

    def update_user_password(self, user_id: int, new_password: str):
        """更新用户密码"""
        sql = "UPDATE users SET password = %s WHERE id = %s"
        result = execute_update(sql, (new_password, user_id))
        self.logger.info(f"更新用户密码 ID：{user_id}")
        return result

    def update_user_status(self, user_id: int, status: int):
        """更新用户状态"""
        sql = "UPDATE users SET status = %s WHERE id = %s"
        result = execute_update(sql, (status, user_id))
        self.logger.info(f"更新用户状态 ID：{user_id} 状态：{status}")
        return result

    def get_all_users(self):
        """获取所有用户"""
        sql = "SELECT * FROM users ORDER BY create_time DESC"
        result = execute_query(sql)
        self.logger.info("查询全部用户列表")
        return result

# 全局单例（整个项目唯一引擎）
engine = ResearchPlatformEngine()

if __name__ == '__main__':
    print(engine.get_user_by_id(1))
    print(engine.get_user_by_phone("13800138000"))