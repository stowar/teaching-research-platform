# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 19:40
"""依赖注入"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend.utils.jwt import get_user_id_from_token,create_access_token
from backend.db.user_db import get_user_by_id

# 定义从哪里获取Token:前端会放在请求头的Authorization字段中,格式是bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    依赖:获取当前登录用户
    所有需要登陆的接口,加上这个依赖即可自动校验token
    """
    # 认证失败的异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码token
    user_id = get_user_id_from_token(token)
    if user_id is None:
        raise credentials_exception

    # 通过解码的token来获取用户信息
    user = get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

async def require_admin(current_user = Depends(get_current_user)):
    """
    依赖:校验是否为管理员
    著有管理员能访问的接口,加上这个依赖
    """
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问",
        )
    return current_user

if __name__ == '__main__':
    token = create_access_token(1)
    get_current_user(token)
    require_admin(token)