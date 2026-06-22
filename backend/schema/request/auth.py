# -*- coding: utf-8 -*-
"""认证模块 Request — 前端 → 后端"""

from pydantic import BaseModel, Field


class UserLogin(BaseModel):
    """登录请求模型（仅手机号+密码）"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")
