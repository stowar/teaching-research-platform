# -*- coding: utf-8 -*-
"""情感分析模块 VO"""

from typing import List
from pydantic import BaseModel


class SentimentResultVO(BaseModel):
    """单条预测结果 VO"""
    sentiment: str
    pos_prob: float
    neg_prob: float
    words: List[str]
    attn_weights: List[float]


class SentimentStatusVO(BaseModel):
    """模型状态 VO"""
    ready: bool
    model_path: str
    device: str
