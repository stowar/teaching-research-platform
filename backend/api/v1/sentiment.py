# -*- coding: utf-8 -*-
"""
教学评价情感分析 API
基于 Hotel_Emotion_Predict 模型（Embedding + BiGRU + Attention）
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from backend.ml.sentiment import predictor

router = APIRouter(prefix="/sentiment", tags=["教学评价情感分析"])


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    sentiment: str
    pos_prob: float
    neg_prob: float
    words: List[str]
    attn_weights: List[float]


@router.post("/predict", response_model=PredictResponse, summary="单条文本情感预测")
def predict_single(req: PredictRequest):
    """
    输入一条教学评价/学生反馈文本，返回情感标签、正负向概率、分词结果与注意力权重。
    注意力权重越高，表示模型越关注该词对情感判断的影响。
    """
    result = predictor.predict(req.text)
    return PredictResponse(**result)


@router.get("/status", summary="模型状态检查")
def model_status():
    """检查情感分析模型是否已加载就绪"""
    return {
        "ready": predictor.is_ready(),
        "model_path": predictor.MODEL_PATH,
        "device": str(predictor.DEVICE)
    }
