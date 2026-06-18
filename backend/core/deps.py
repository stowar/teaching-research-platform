# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 19:40
"""依赖注入"""
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from backend.utils.jwt import get_user_id_from_token
from backend.db.user_db import get_user_by_id
from backend.core.exceptions import BusinessException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    依赖:获取当前登录用户
    所有需要登陆的接口,加上这个依赖即可自动校验token
    """
    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise BusinessException("无效的认证凭证", code=status.HTTP_401_UNAUTHORIZED)

    user = get_user_by_id(user_id)
    if user is None:
        raise BusinessException("用户不存在", code=status.HTTP_401_UNAUTHORIZED)

    if user.status != 1:
        raise BusinessException("账号已被禁用", code=status.HTTP_403_FORBIDDEN)

    return user


async def require_admin(current_user=Depends(get_current_user)):
    """
    依赖:校验是否为管理员
    著有管理员能访问的接口,加上这个依赖
    """
    if current_user.role != "admin":
        raise BusinessException("无权访问", code=status.HTTP_403_FORBIDDEN)
    return current_user
