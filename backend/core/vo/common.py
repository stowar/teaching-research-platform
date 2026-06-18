# -*- coding: utf-8 -*-
"""统一响应信封 — ApiResponse 泛型包装"""

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """所有 API 返回的统一包装"""
    code: int = 200
    msg: str = "ok"
    data: Optional[T] = None
