# -*- coding: utf-8 -*-
"""
教学评价情感分析 API
基于 Hotel_Emotion_Predict 模型（Embedding + BiGRU + Attention）
"""
from fastapi import APIRouter
from pydantic import BaseModel

from backend.ml.sentiment import predictor
from backend.core.vo.common import ApiResponse
from backend.core.vo.sentiment import SentimentResultVO, SentimentStatusVO

router = APIRouter(prefix="/sentiment", tags=["教学评价情感分析"])


class PredictRequest(BaseModel):
    text: str


@router.post("/predict", response_model=ApiResponse[SentimentResultVO], summary="单条文本情感预测")
def predict_single(req: PredictRequest):
    """输入一条教学评价文本，返回情感标签、正负向概率、分词结果与注意力权重"""
    result = predictor.predict(req.text)
    return ApiResponse(data=SentimentResultVO(**result))


@router.get("/status", response_model=ApiResponse[SentimentStatusVO], summary="模型状态检查")
def model_status():
    """检查情感分析模型是否已加载就绪"""
    return ApiResponse(data=SentimentStatusVO(
        ready=predictor.is_ready(),
        model_path=predictor.MODEL_PATH,
        device=str(predictor.DEVICE),
    ))
