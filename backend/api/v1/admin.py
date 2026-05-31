from fastapi import APIRouter, Depends, HTTPException

from backend.core.deps import require_admin
from backend.core.exceptions import BusinessException
from backend.services.admin import (
    get_all_user_list_service, admin_get_user_info_service, admin_update_user_info_service,delete_user_service,enable_user_service
)
from backend.model.user import UserUpdate

# 初始化路由
router_admin = APIRouter(prefix="/admin", tags=["管理员"])


@router_admin.get("/", summary="管理员-获取所有用户信息")
def get_all_user_list(admin = Depends(require_admin)):
    """管理员-获取所有用户信息"""
    try:
        return get_all_user_list_service()
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router_admin.get("/{user_id}", summary="管理员-获取指定用户信息")
def admin_get_user_info(user_id: int, admin = Depends(require_admin)):
    """管理员-获取指定用户信息"""
    try:
        return admin_get_user_info_service(user_id)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router_admin.put("/{user_id}", summary="管理员-更新指定用户信息")
def admin_update_user_info(user_id: int, update_data: UserUpdate, admin = Depends(require_admin)):
    """管理员-更新指定用户信息"""
    try:
        return admin_update_user_info_service(user_id, update_data)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router_admin.delete("/{user_id}", summary="管理员-禁用/删除用户")
def delete_user(user_id: int, admin = Depends(require_admin)):
    """管理员-禁用/删除用户"""
    try:
        return delete_user_service(user_id)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)

@router_admin.put("/enable/{user_id}", summary="管理员-解封用户")
def enable_user(user_id: int, admin=Depends(require_admin)):
    """管理员-解封用户"""
    try:
        return enable_user_service(user_id)
    except BusinessException as e:
        raise HTTPException(status_code=e.code, detail=e.message)
