from backend.core.exceptions import BusinessException
from backend.db import user_db
from backend.core.security import verify_password, get_password_hash


def update_current_user_info_service(update_data, current_user: dict):
    """更新当前登录用户的个人信息"""
    if not update_data or not any([update_data.name, update_data.school, update_data.title]):
        raise BusinessException("没有需要更新的字段", code=400)

    user_db.update_user_info(current_user["id"], update_data)
    r_updated_user = user_db.get_user_by_id(current_user["id"])
    return {
        "code": 200,
        "msg": "更新成功",
        "data": r_updated_user
    }

def update_password_service(password_data, current_user: dict) -> dict:
    """修改当前登录用户的密码"""
    if not verify_password(password_data.old_password, current_user["password"]):
        raise BusinessException("原密码错误", code=400)

    new_hashed_password = get_password_hash(password_data.new_password)
    user_db.update_user_password(current_user["id"], new_hashed_password)
    return {
        "code": 200,
        "msg": "修改成功"
    }