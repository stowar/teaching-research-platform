# -*- coding: utf-8 -*-
# @Time    : 2026/5/12 21:20

"""用户管理模块"""

from fastapi import APIRouter, Depends

from backend.core.deps import get_current_user
from backend.core.vo.common import ApiResponse
from backend.core.vo.user import UserVO, to_user_vo
from backend.services.users import update_current_user_info_service, update_password_service
from backend.model.user import UserUpdate, UserUpdatePassword


router_user = APIRouter(prefix="/users", tags=["用户管理"])


@router_user.get("/me", summary="获取当前用户信息", response_model=ApiResponse[UserVO])
def get_current_user_info(current_user=Depends(get_current_user)):
    return ApiResponse(data=to_user_vo(current_user))


@router_user.put("/me", summary="更新当前用户信息", response_model=ApiResponse[UserVO])
def update_current_user_info(update_data: UserUpdate, current_user=Depends(get_current_user)):
    return update_current_user_info_service(update_data, current_user)


@router_user.put("/password", summary="修改当前用户密码", response_model=ApiResponse)
def update_password(password_data: UserUpdatePassword, current_user=Depends(get_current_user)):
    return update_password_service(password_data, current_user)


