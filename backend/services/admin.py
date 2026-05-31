from backend.core.exceptions import BusinessException
from backend.db import user_db
from backend.model.user import UserUpdate
def get_all_user_list_service() -> dict:
    """获取所有用户的信息，仅管理员可访问"""
    users = user_db.get_all_users()
    if not users:
        raise BusinessException("用户不存在", code=404)
    return {
        "code": 200,
        "msg": "查询成功",
        "data": users
    }


def admin_get_user_info_service(user_id: int) -> dict:
    """管理员-获取指定用户信息"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    return {
        "code": 200,
        "msg": "查询成功",
        "data": [user]
    }


def admin_update_user_info_service(user_id: int, info: UserUpdate) -> dict:
    """管理员-更新指定用户信息"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)

    user_db.update_user_info(user_id, info)
    updated_user = user_db.get_user_by_id(user_id)
    return {
        "code": 200,
        "msg": "更新成功",
        "data": updated_user
    }

def delete_user_service(user_id: int) -> dict:
    """管理员禁用指定用户（逻辑删除，设置status=0）"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)

    # 禁止删除管理员账号
    if user["role"] == "admin":
        raise BusinessException("管理员账号不能被禁用", code=400)

    # 设置用户状态为0(禁用)
    user_db.update_user_status(user_id, 0)
    return {
        "code": 200,
        "msg": "禁用成功",
        "data": user_db.get_user_by_id(user_id)
    }

def enable_user_service(user_id: int) -> dict:
    """解封账号"""
    user = user_db.get_user_by_id(user_id)
    if not user:
        raise BusinessException("用户不存在", code=404)
    user_db.update_user_status(user_id, 1)
    return {
        "code": 200,
        "msg": "启用成功",
        "data": user_db.get_user_by_id(user_id)
    }

