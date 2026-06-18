# -*- coding: utf-8 -*-
# @Time    : 2025/5/12 20:00

"""登录/注册接口"""

from fastapi import APIRouter

from backend.model.user import UserCreate
from backend.model.auth import UserLogin
from backend.services.auth import login_service, register_service
from backend.core.vo.common import ApiResponse
from backend.core.vo.user import LoginVO, UserVO

router = APIRouter(prefix="/auth", tags=["认证授权"])


@router.post("/login", response_model=ApiResponse[LoginVO], summary="用户登录")
def login(login_data: UserLogin):
    return login_service(login_data.phone, login_data.password)


@router.post("/register", response_model=ApiResponse[UserVO], summary="用户注册")
def register(register_data: UserCreate):
    return register_service(register_data)



