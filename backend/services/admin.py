from __future__ import annotations

from backend.core.exceptions import BusinessException
from backend.schema.vo.common import ApiResponse
from backend.schema.vo.user import UserVO, to_user_vo
from backend.db import user_db
from backend.schema.request.user import UserUpdate


def get_all_user_list_service() -> ApiResponse[list[UserVO]]:
    """获取所有用户的信息，仅管理员可访问"""
    users = user_db.get_all_users()
    if not users:
        raise BusinessException("用户不存在", code=404)
    return ApiResponse(
        msg="查询成功",
        data=[to_user_vo(u) for u in users],
    )


def admin_get_user_info_service(user_id: int) -> ApiResponse[UserVO]:
    """管理员-获取指定用户信息"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    return ApiResponse(
        msg="查询成功",
        data=to_user_vo(user),
    )


def admin_update_user_info_service(user_id: int, info: UserUpdate) -> ApiResponse[UserVO]:
    """管理员-更新指定用户信息"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    user_db.update_user_info(user_id, info)
    return ApiResponse(
        msg="更新成功",
        data=to_user_vo(user_db.get_user_by_id(user_id)),
    )


def delete_user_service(user_id: int) -> ApiResponse[UserVO]:
    """管理员禁用指定用户（逻辑删除，设置status=0）"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    if user.role == "admin":
        raise BusinessException("管理员账号不能被禁用", code=400)
    user_db.update_user_status(user_id, 0)
    return ApiResponse(
        msg="禁用成功",
        data=to_user_vo(user_db.get_user_by_id(user_id)),
    )


def enable_user_service(user_id: int) -> ApiResponse[UserVO]:
    """解封账号"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    user_db.update_user_status(user_id, 1)
    return ApiResponse(
        msg="启用成功",
        data=to_user_vo(user_db.get_user_by_id(user_id)),
    )

