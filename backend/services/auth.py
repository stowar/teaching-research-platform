# -*- coding: utf-8 -*-
"""认证业务层：处理登录、注册的核心业务逻辑"""

from backend.core.exceptions import BusinessException
from backend.core.security import verify_password, get_password_hash
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.user import UserVO, LoginVO, to_user_vo
from backend.db import user_db
from backend.utils.jwt import create_access_token


def login_service(phone: str, password: str) -> ApiResponse[LoginVO]:
    """用户登录 — 返回 ApiResponse[LoginVO]"""
    user = user_db.get_user_by_phone(phone)
    if not user:
        raise BusinessException("用户不存在", code=400)

    if not verify_password(password, user.password):
        raise BusinessException("密码错误", code=401)

    access_token = create_access_token(user.id)

    return ApiResponse(
        msg="登录成功",
        data=LoginVO(
            access_token=access_token,
            user=to_user_vo(user),
        ),
    )


def register_service(user_data) -> ApiResponse[UserVO]:
    """用户注册 — 返回 ApiResponse[UserVO]"""
    if user_db.get_user_by_phone(user_data.phone):
        raise BusinessException("手机号已注册", code=400)

    if not user_data.name:
        user_data.name = "新用户"

    user_db.create_user(user_data)
    new_user = user_db.get_user_by_phone(user_data.phone)

    return ApiResponse(
        msg="注册成功",
        data=to_user_vo(new_user),
    )
