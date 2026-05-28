# -*- coding: utf-8 -*-
# @Time    : 2026/5/12 21:20

"""用户管理模块"""

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from backend.core.deps import get_current_user
from backend.db.user_db import (update_user_info,update_user_password)
from backend.model.user import UserResponse,UserUpdate,UserUpdatePassword


# 初始化路由
router_user = APIRouter(prefix="/users", tags=["用户管理"])

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================  用户接口 ===============================
@router_user.get("/me", summary="获取当前用户信息", response_model=UserResponse)
def get_current_user_info(current_user = Depends(get_current_user)):
    """获取当前登录用户的个人信息"""
    return current_user


@router_user.put("/me", summary="更新当前用户信息")
def update_current_user_info(
    update_data: UserUpdate,
    current_user = Depends(get_current_user)
):
    """更新当前登录用户的个人信息"""
    # 更新数据库
    updated_user = update_user_info(current_user["id"], update_data)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有需要更新的字段")
    return {
        "code": 200,
        "msg": "更新成功"
    }


@router_user.put("/password", summary="修改当前用户密码")
def change_password(password_data: UserUpdatePassword,current_user = Depends(get_current_user)):

    """修改当前登录用户的密码"""
    # 验证原密码是否正确
    if not pwd_context.verify(password_data.old_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="原密码错误")

    # 加密新密码并更新
    new_hashed_password = pwd_context.hash(password_data.new_password)
    update_user_password(current_user["id"], new_hashed_password)
    return {
        "code": 200,
        "msg": "修改成功"
    }



if __name__ == '__main__':
    update_current_user_info(UserUpdate(name="测试用户", school="测试学校", title="教师"))
