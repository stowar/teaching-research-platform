# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 20:00

"""登录/注册接口"""

from fastapi import APIRouter,HTTPException,status
from passlib.context import CryptContext

from backend.db.user_db import get_user_by_phone,create_user
from backend.utils.jwt import create_access_token
from backend.model.user import UserResponse,UserCreate,LoginResponse,UserLogin,BaseResponse

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 创建路由的作用是创建接口
router = APIRouter(prefix="/auth", tags=["认证授权"])

@router.post("/login", response_model=LoginResponse,summary="用户登录")
def login(login_data: UserLogin):
    """
    用户登录接口
    - 接收手机号和密码
    - 校验用户存在性和密码正确性
    - 返回JWT令牌和用户信息
    """
    # 1.根据手机好查询客户
    user = get_user_by_phone(login_data.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在"
        )
    # 2.校验密码
    if not pwd_context.verify(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="密码错误"
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


@router.post("/register", summary="用户注册", response_model=BaseResponse)
def register(register_data: UserCreate):
    """用户注册接口"""
    if get_user_by_phone(register_data.phone):
        raise HTTPException(status_code=400, detail="手机号已注册")

    new_user = create_user(register_data)
    return {
        "code": 200,
        "msg": "注册成功"
    }


if __name__ == '__main__':
    # print(login(UserLogin(phone="13800138000", password="123456")))
    print(register(UserCreate(
        phone="13810114001",
        name="测试用户",
        password="123456",
        school="测试学校",
        title="老师"
    )))

