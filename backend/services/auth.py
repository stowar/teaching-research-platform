from passlib.context import CryptContext
from backend.core.engine import engine
from fastapi import APIRouter,HTTPException,status
from passlib.context import CryptContext
from backend.core.engine import engine

from backend.utils.jwt import create_access_token

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def login_service(phone: str, password: str) -> dict:
    """
    用户登录接口
    - 接收手机号和密码
    - 校验用户存在性和密码正确性
    - 返回JWT令牌和用户信息
    """

    # 1.根据手机好查询客户
    user = engine.get_user_by_phone(phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在"
        )
    # 2.校验密码
    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="密码错误"
        )

    # 3.生成JWT令牌
    access_token = create_access_token(user["id"])

    # 4.返回结果
    return {
        "msg": "登录成功",
        "access_token": access_token,
        "token_type": "Bearer <token>",
        "user": user
    }

def register_service(user_data):
    """用户注册"""
    if engine.get_user_by_phone(user_data.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")

    engine.create_user(user_data)
    new_user = engine.get_user_by_phone(user_data.phone)

    return {
        "code": 200,
        "msg": "注册成功",
        "data": new_user
    }