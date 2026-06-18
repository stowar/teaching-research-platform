from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from backend.core.deps import require_admin
from backend.core.vo.common import ApiResponse
from backend.core.vo.user import UserVO
from backend.services.admin import (
    get_all_user_list_service, admin_get_user_info_service,
    admin_update_user_info_service, delete_user_service, enable_user_service,
)
from backend.model.user import UserUpdate

router_admin = APIRouter(prefix="/admin", tags=["管理员"])


@router_admin.get("/", summary="管理员-获取所有用户信息", response_model=ApiResponse[List[UserVO]])
def get_all_user_list(admin=Depends(require_admin)):
    return get_all_user_list_service()


@router_admin.get("/{user_id}", summary="管理员-获取指定用户信息", response_model=ApiResponse[UserVO])
def admin_get_user_info(user_id: int, admin=Depends(require_admin)):
    return admin_get_user_info_service(user_id)


@router_admin.put("/{user_id}", summary="管理员-更新指定用户信息", response_model=ApiResponse[UserVO])
def admin_update_user_info(user_id: int, update_data: UserUpdate, admin=Depends(require_admin)):
    return admin_update_user_info_service(user_id, update_data)


@router_admin.delete("/{user_id}", summary="管理员-禁用/删除用户", response_model=ApiResponse[UserVO])
def delete_user(user_id: int, admin=Depends(require_admin)):
    return delete_user_service(user_id)


@router_admin.put("/enable/{user_id}", summary="管理员-解封用户", response_model=ApiResponse[UserVO])
def enable_user(user_id: int, admin=Depends(require_admin)):
    return enable_user_service(user_id)
