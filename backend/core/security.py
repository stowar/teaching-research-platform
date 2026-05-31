# -*- coding: utf-8 -*-
"""安全工具模块：集中管理密码加密与验证"""

from passlib.context import CryptContext

# 配置bcrypt加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希密码匹配
    :param plain_password: 用户输入的明文密码
    :param hashed_password: 数据库存储的哈希密码
    :return: 匹配返回True，否则False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码的bcrypt哈希值
    :param password: 明文密码
    :return: 加密后的哈希字符串
    """
    return pwd_context.hash(password)
