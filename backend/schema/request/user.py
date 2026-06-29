# -*- coding: utf-8 -*-
"""用户模块 Request — 前端 → 后端"""

from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """用户公共基础字段（所有用户模型的父类）"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    name: Optional[str] = Field(..., max_length=20, description="用户名")
    school: Optional[str] = Field(None, max_length=100, description="学校")
    title: Optional[str] = Field(None, max_length=100, description="职称")


class UserCreate(UserBase):
    """注册/创建用户请求模型（继承 UserBase + 密码）"""
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
