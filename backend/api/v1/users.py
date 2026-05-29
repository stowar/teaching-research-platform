# -*- coding: utf-8 -*-
# @Time    : 2026/5/12 21:20

"""用户管理模块"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.exceptions import BusinessException
from backend.core.deps import get_current_user
from backend.services.users import update_current_user_info_service,update_password_service
from backend.model.user import UserResponse,UserUpdate,UserUpdatePassword


# 初始化路由
router_user = APIRouter(prefix="/users", tags=["用户管理"])

# ==============================  用户接口 ===============================
@router_user.get("/me", summary="获取当前用户信息", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前登录用户的个人信息"""
    return current_user


@router_user.put("/me", summary="更新当前用户信息")
def update_current_user_info(update_data: UserUpdate,current_user=Depends(get_current_user)):
    """更新当前登录用户的个人信息"""
    try:
        return update_current_user_info_service(update_data,current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router_user.put("/password", summary="修改当前用户密码")
def update_password(password_data: UserUpdatePassword, current_user=Depends(get_current_user)):
    """修改当前登录用户的密码"""
    try:
        return update_password_service(password_data, current_user)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


if __name__ == '__main__':
    update_current_user_info(UserUpdate(name="测试用户", school="测试学校", title="教师"))
