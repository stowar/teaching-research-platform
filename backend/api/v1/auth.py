# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 20:00

"""登录/注册接口"""

from fastapi import APIRouter,HTTPException,status

from backend.model.user import UserCreate,LoginResponse
from backend.model.auth import UserLogin
from backend.services.auth import login_service,register_service
from backend.core.exceptions import BusinessException

# 创建路由的作用是创建接口
router = APIRouter(prefix="/auth", tags=["认证授权"])


@router.post("/login", response_model=LoginResponse,summary="用户登录")
def login(login_data: UserLogin):
    """用户登录接口"""
    try:
        return login_service(login_data.phone, login_data.password)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.post("/register", summary="用户注册")
def register(register_data: UserCreate):
    """用户注册接口"""
    try:
        new_user = register_service(register_data)
        return new_user
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


if __name__ == '__main__':
    # print(login(UserLogin(phone="13800138000", password="123456")))
    print(register(UserCreate(
        phone="13811114101",
        name="测试用户",
        password="123456",
        school="测试学校",
        title="老师"
    )))

