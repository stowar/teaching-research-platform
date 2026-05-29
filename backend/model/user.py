# -*- coding: utf-8 -*-
# @Time    : 2026/5/11 22:09
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ======================
# 1. 用户基础模型（公共字段抽取）
# ======================
class UserBase(BaseModel):
    """用户公共基础字段（所有用户模型的父类）"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    name: str = Field(..., max_length=20, description="用户名")
    school: Optional[str] = Field(None, max_length=100, description="学校")
    title: Optional[str] = Field(None, max_length=100, description="职称")


# ======================
# 2. 请求模型（前端 → 后端）
# ======================
class UserCreate(UserBase):
    """注册/创建用户请求模型（继承UserBase + 密码）"""
    password: str = Field(..., min_length=6, max_length=20, description="密码")





class UserUpdate(BaseModel):
    """修改个人信息（无需手机号，仅可修改姓名/学校/职称）"""
    name: Optional[str] = Field(None, max_length=20, description="用户名")
    school: Optional[str] = Field(None, max_length=100, description="学校")
    title: Optional[str] = Field(None, max_length=100, description="职称")


class UserUpdatePassword(BaseModel):
    """修改密码（仅需新旧密码）"""
    old_password: str = Field(..., min_length=6, max_length=20, description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=20, description="新密码")


# ======================
# 3. 响应模型（后端 → 前端，脱敏返回）
# ======================
class BaseResponse(BaseModel):
    """返回code和msg"""
    code: int = 200
    msg: Optional[str] = Field(None, description="提示信息")

class UserResponse(UserBase):
    """用户完整响应模型（不含密码）"""
    id: int
    role: str       # 角色：user/admin
    status: int      # 状态：1正常 0禁用
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True  # 兼容数据库 ORM 对象

class LoginResponse(BaseResponse):
    """登录响应（Token + 用户信息）"""
    access_token: str
    token_type: str = "Bearer <token>"
    user: UserResponse