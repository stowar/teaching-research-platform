# -*- coding: utf-8 -*-
"""认证业务层：处理登录、注册的核心业务逻辑"""

from backend.core.exceptions import BusinessException
from backend.core.security import verify_password, get_password_hash
from backend.db import user_db
from backend.utils.jwt import create_access_token


def login_service(phone: str, password: str) -> dict:
    """
    用户登录服务
    - 校验用户存在性和密码正确性
    - 返回JWT令牌和用户信息
    """
    user = user_db.get_user_by_phone(phone)
    if not user:
        raise BusinessException("用户不存在", code=400)

    if not verify_password(password, user["password"]):
        raise BusinessException("密码错误", code=401)

    access_token = create_access_token(user["id"])

    return {
        "msg": "登录成功",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


def register_service(user_data) -> dict:
    """用户注册服务"""
    if user_db.get_user_by_phone(user_data.phone):
        raise BusinessException("手机号已注册", code=400)

    user_db.create_user(user_data)
    new_user = user_db.get_user_by_phone(user_data.phone)

    return {
        "code": 200,
        "msg": "注册成功",
        "data": new_user
    }
