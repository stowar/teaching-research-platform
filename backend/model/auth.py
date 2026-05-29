# backend/schemas/auth.py
from pydantic import Field,BaseModel

# 登录请求
class UserLogin(BaseModel):
    """登录请求模型（仅手机号+密码）"""
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    password: str = Field(..., min_length=6, max_length=20, description="密码")

