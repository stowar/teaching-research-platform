# -*- coding: utf-8 -*-
# @Time    : 2026/5/11 22:09
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ======================
# 0. DO：数据库表行完整映射（仅供 DB / Service 层使用，API 层禁入）
# ======================
class UserDO(BaseModel):
    """users 表完整行 — 含 password，仅内部流转"""
    id: int
    phone: str
    password: str
    name: Optional[str] = None
    school: Optional[str] = None
    title: Optional[str] = None
    role: str
    status: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


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


