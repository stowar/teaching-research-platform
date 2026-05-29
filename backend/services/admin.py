from fastapi import HTTPException, status
from backend.core.engine import engine
def get_all_user_list_service()->dict:
    """获取所有用户的信息，仅管理员可访问"""
    users = engine.get_all_users()
    if not users:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "msg": "启用成功",
        "data": users
    }


def admin_get_user_info_service(user_id: int) -> dict:
    """管理员-获取指定用户信息"""
    user = engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        "code": 200,
        "msg": "查询成功",
        "data": [user]
    }


def admin_update_user_info_service(user_id: int,info: dict) -> dict:
    """管理员-更新指定用户信息"""
    # 检查用户是否存在
    user = engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 更新用户信息
    engine.update_user_info(user_id, info)
    updated_user = engine.get_user_by_id(user_id)
    return {
        "code": 200,
        "msg": "更新成功",
        "data": updated_user
    }

def delete_user_service(user_id: int) -> dict:
    """管理员禁用指定用户（逻辑删除，设置status=0）"""
    user = engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 禁止删除管理员账号
    if user["role"] == "admin":
        raise HTTPException(status_code=400, detail="管理员账号不能被禁用")

    # 设置用户状态为0(禁用)
    engine.update_user_status(user_id, 0)
    return {
        "code": 200,
        "msg": "禁用成功",
        "data": engine.get_user_by_id(user_id)
    }

def enable_user_service(user_id: int) -> dict:
    """解封账号"""
    user = engine.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    engine.update_user_status(user_id, 1)
    return {
        "code": 200,
        "msg": "启用成功",
        "data": engine.get_user_by_id(user_id)
    }

