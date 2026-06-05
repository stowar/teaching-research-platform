# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 19:00
"""
实现生成令牌、验证令牌、解析用户 ID
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
# 用来安全的安全地生成、解析、验证 JWT 令牌
from jose import JWTError,jwt

from backend.core.config import settings

def create_access_token(user_id: int) -> str:
    """
    生成JWT访问令牌
    :param user_id:用户id(唯一表示)
    :return:
    """
    # 1.准备令牌载荷(只存用户id)
    # datetime.utcnow(): 获取UTC时间
    # timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)：创建一个时间间隔对象
    # expire：令牌过期时间
    expire = datetime.now(timezone.utc) + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode ={"sub": str(user_id),"exp": expire}

    # 2.用密钥和加密算法生成令牌
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> bool:
    """
    验证令牌是否有效
    :param token:前端传过来的JWT令牌
    :return: True有效,False无效
    """
    try:
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return True
    except JWTError:
        return False


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    从令牌中解析出用户ID
    :param token:前端传过来的JWT令牌
    :return:用户ID，无效则返回None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # print(payload) # 字典
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
        return None

if __name__ == '__main__':
    token = create_access_token(1)
    print("真实Token:", token)
    print("是否有效:", verify_token(token))
    print("解析出的ID:", get_user_id_from_token(token))