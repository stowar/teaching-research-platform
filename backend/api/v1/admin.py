from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from backend.core.deps import require_admin
from backend.db.user_db import (get_user_by_id,update_user_info,get_all_users,update_user_status)
from backend.model.user import UserResponse,UserUpdate,UserUpdatePassword

# 初始化路由
router_admin = APIRouter(prefix="/admin", tags=["管理员"])
# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================== 管理员接口 ==============================
@router_admin.get("/", summary="管理员-获取所有用户信息")
def get_all_user_list(admin=Depends(require_admin)):
    """获取所有用户的信息，仅管理员可访问"""
    users = get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "msg": "启用成功",
        "data": users
    }


@router_admin.get("/{user_id}", summary="管理员-获取指定用户信息")
def admin_get_user_info(user_id: int, admin = Depends(require_admin)):
    """管理员-获取指定用户信息"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "msg": "启用成功",
        "data": [user]
    }


@router_admin.put("/{user_id}", summary="管理员-更新指定用户信息")
def admin_update_user_info(user_id: int, update_data: UserUpdate, admin = Depends(require_admin)):
    """管理员-更新指定用户信息"""
    # 检查用户是否存在
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新用户信息
    updated_user = update_user_info(user_id, update_data)
    return {
        "code": 200,
        "msg": "更新成功",
        "data": updated_user
    }


@router_admin.delete("/{user_id}", summary="管理员-禁用/删除用户")
def delete_user(user_id: int, admin = Depends(require_admin)):
    """管理员禁用指定用户（逻辑删除，设置status=0）"""
    # 检查用户是否存在
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 禁止删除管理员账号
    if user["role"] == "admin":
        raise HTTPException(status_code=400, detail="管理员账号不能被禁用")

    # 设置用户状态为0(禁用)
    update_user_status(user_id, 0)
    return {
        "code": 200,
        "msg": "禁用成功",
        "data": get_user_by_id(user_id)
    }

@router_admin.put("/enable/{user_id}", summary="管理员-解封用户")
def de_delete_user(user_id: int, admin = Depends(require_admin)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    update_user_status(user_id, 1)
    return {
        "code": 200,
        "msg": "启用成功",
        "data": get_user_by_id(user_id)
    }