# -*- coding: utf-8 -*-
"""用户模块 VO — 仅 API / Service 层使用"""

from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from backend.schema.do.user import UserDO


class UserVO(BaseModel):
    """用户信息 VO — 不含密码，含格式化标签"""
    id: int
    phone: str
    name: Optional[str] = None
    school: Optional[str] = None
    title: Optional[str] = None
    role: str
    role_label: str
    status: int
    create_time: str
    update_time: str


class LoginVO(BaseModel):
    """登录响应 VO"""
    access_token: str
    token_type: str = "bearer"
    user: UserVO


def to_user_vo(u: "UserDO") -> UserVO:
    """UserDO → UserVO 转换，脱敏 + 格式化（供 Service 层调用）"""
    def _fmt(dt):
        return dt.strftime("%Y-%m-%d %H:%M") if dt else ""

    return UserVO(
        id=u.id,
        phone=u.phone,
        name=u.name,
        school=u.school,
        title=u.title,
        role=u.role,
        role_label="管理员" if u.role == "admin" else "教师",
        status=u.status,
        create_time=_fmt(u.create_time),
        update_time=_fmt(u.update_time),
    )
