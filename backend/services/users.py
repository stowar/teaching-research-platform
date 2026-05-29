
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext

from backend.core.engine import engine
from backend.core.deps import get_current_user
from backend.model.user import UserResponse,UserUpdate,UserUpdatePassword

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def update_current_user_info_service(update_data: dict,current_user: dict,):
    """更新当前登录用户的个人信息"""
    updated_user = engine.update_user_info(current_user["id"], update_data)
    r_updated_user = engine.get_user_by_id(current_user["id"])
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="没有需要更新的字段")
    return {
        "code": 200,
        "msg": "更新成功",
        "data": r_updated_user
    }

def update_password_service(password_data: dict,current_user: dict) -> dict:
    """修改当前登录用户的密码"""
    if not pwd_context.verify(password_data.old_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="原密码错误")

    # 加密新密码并更新
    new_hashed_password = pwd_context.hash(password_data.new_password)
    engine.update_user_password(current_user["id"], new_hashed_password)
    return {
        "code": 200,
        "msg": "修改成功"
    }