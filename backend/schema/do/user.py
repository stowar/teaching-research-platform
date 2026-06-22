# -*- coding: utf-8 -*-
"""用户模块 DO — users 表完整行，含 password，仅 DB/Service 层内部流转"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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
