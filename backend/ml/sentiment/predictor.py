# -*- coding: utf-8 -*-
"""
Sentiment Predictor: 懒加载模型，线程安全，支持单条预测 + 注意力权重输出
"""
import os
import json
import threading
import torch
import torch.nn.functional as F

from backend.ml.sentiment.model import SentimentGRU
from backend.ml.sentiment.data_process import normalize_string
from backend.core.config import settings

# 全局单例状态
_model = None
_word2index = None
_index2word = None
_lock = threading.Lock()

# 配置常量
ASSETS_DIR = os.path.join(settings.BASE_DIR, "backend", "ml", "sentiment", "assets")
MODEL_PATH = os.path.join(ASSETS_DIR, "model.pt")
WORD2INDEX_PATH = os.path.join(ASSETS_DIR, "word2index.json")

MAX_SEQ_LEN = 50
EMBEDDING_DIM = 128
HIDDEN_SIZE = 256
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_model():
    """懒加载模型与词典（线程安全，词典从 JSON 加载保证与训练时一致）"""
    global _model, _word2index, _index2word
    if _model is not None:
        return _model, _word2index, _index2word

    with _lock:
        if _model is not None:
            return _model, _word2index, _index2word

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"模型文件不存在: {MODEL_PATH}")
        if not os.path.exists(WORD2INDEX_PATH):
            raise RuntimeError(f"词典文件不存在: {WORD2INDEX_PATH}")

        # 加载训练时保存的词典（保证 vocab_size 与模型一致）
        with open(WORD2INDEX_PATH, "r", encoding="utf-8") as f:
            _word2index = json.load(f)

        vocab_size = len(_word2index)
        model = SentimentGRU(
            vocab_size=vocab_size,
            embedding_dim=EMBEDDING_DIM,
            hidden_size=HIDDEN_SIZE,
            num_layers=2,
            dropout=0.5,
            pad_idx=0
        )

        state_dict = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
        model.load_state_dict(state_dict)
        model.to(DEVICE)
        model.eval()

        _model = model
        return _model, _word2index, _index2word


def predict(text: str):
    """
    单条文本情感预测
    :param text: 输入文本
    :return: dict {
        sentiment: str,
        pos_prob: float,
        neg_prob: float,
        words: list[str],
        attn_weights: list[float]
    }
    """
    model, word2index, index2word = _load_model()

    # 预处理
    words = normalize_string(text)
    if not words:
        return {
            "sentiment": "无法判断",
            "pos_prob": 0.0,
            "neg_prob": 0.0,
            "words": [],
            "attn_weights": []
        }

    # 词转索引
    x = [word2index.get(word, 1) for word in words]  # 1 = <UNK>

    # 截断与填充
    if len(x) > MAX_SEQ_LEN:
        x = x[:MAX_SEQ_LEN]
        words = words[:MAX_SEQ_LEN]
    original_len = len(x)
    x += [0] * (MAX_SEQ_LEN - len(x))  # 0 = <PAD>

    tensor_x = torch.tensor(x, dtype=torch.long, device=DEVICE).unsqueeze(0)

    with torch.no_grad():
        output, attn_weights = model(tensor_x)

    probs = F.softmax(output, dim=1)
    neg_prob = float(probs[0][0])
    pos_prob = float(probs[0][1])
    sentiment = "正面好评" if pos_prob > neg_prob else "负面差评"

    # 提取有效词的注意力权重（去掉填充部分）
    # 不做归一化 — 保留原始 softmax 分布，模型内部 attention 层已做 softmax
    attn = attn_weights.squeeze(0).squeeze(1).cpu().numpy().tolist()
    attn = [round(a, 6) for a in attn[:original_len]]

    return {
        "sentiment": sentiment,
        "pos_prob": round(pos_prob, 4),
        "neg_prob": round(neg_prob, 4),
        "words": words,
        "attn_weights": attn
    }


def is_ready() -> bool:
    """检查模型是否已就绪"""
    return os.path.exists(MODEL_PATH) and os.path.exists(WORD2INDEX_PATH)
