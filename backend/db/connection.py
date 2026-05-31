# -*- coding: utf-8 -
# @Time    : 2023/5/27 16:05

import pymysql
from pymysql.cursors import DictCursor
from backend.core.config import settings


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=str(settings.DB_PASSWORD).encode('utf-8').decode('latin-1'),
        db=settings.DB_NAME,
        charset='utf8mb4',
        cursorclass=DictCursor
    )

def execute_query(sql,params=None):
    """执行查询语句,返回结果列表"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()

def execute_one(sql,params=None):
    """执行单条语句,返回单条结果"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        conn.close()

def execute_update(sql,params=None):
    """执行增删改语句,返回受影响的行数"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


if __name__ == '__main__':

    sql = "SELECT * FROM users"
    users = execute_query(sql)
    print(users)

    sql = "SELECT * FROM users WHERE id = %s"
    user = execute_one(sql, (1,))
    print(user)

    # sql = "UPDATE users SET name = %s WHERE id = %s"
    # execute_update(sql, ("最高权限管理员", 1))
    # print( "更新成功")
