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

    # 短文本规则兜底：≤3 个词的输入走关键词匹配，神经网络在极端短文本上不可靠
    if words and len(words) <= 3:
        # jieba 可能把短词切成单字，用原始文本补一刀
        raw_text = text.replace(' ', '').strip()
        # 强信号词：单字/双字，含义非常明确 → 95% 置信
        strong_pos = {'好','很好','棒','赞','优秀','不错','认真','用心','负责','专业','值得','推荐','喜欢'}
        strong_neg = {'差','差评','差劲','烂','糟糕','垃圾','水','糊弄','敷衍','无聊','失望','无语','枯燥','别选'}
        # 弱信号词：需要上下文才能确定 → 65% 置信
        weak_pos = {'还行','还可以','可以','挺好','满意','给力','靠谱','有趣','学到了'}
        weak_neg = {'不好','不行','不怎么样','没意思','没劲','不值','后悔','浪费时间','听不懂'}

        score = 0
        is_strong = False
        for w in words + [raw_text]:  # 把原始文本也放进去兜底 jieba 分词的误切割
            if w in strong_pos:
                score += 1; is_strong = True
            elif w in strong_neg:
                score -= 1; is_strong = True
            elif w in weak_pos:
                score += 1
            elif w in weak_neg:
                score -= 1

        conf = 0.95 if is_strong else 0.65
        if score > 0:
            pos_prob, neg_prob = conf, round(1 - conf, 4)
        elif score < 0:
            pos_prob, neg_prob = round(1 - conf, 4), conf
        else:
            pos_prob = neg_prob = 0.50

        if pos_prob > 0.65: sentiment = "强好评"
        elif pos_prob > 0.50: sentiment = "温和正面"
        elif pos_prob > 0.35: sentiment = "中性评价"
        else: sentiment = "差评"

        return {"sentiment":sentiment,"pos_prob":pos_prob,"neg_prob":neg_prob,"words":words,"attn_weights":[1.0/len(words)]*len(words)}

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

    # 温度缩放：当注意力分布均匀（高熵）时加大温度，让模型不那么"自信"
    raw_probs = F.softmax(output, dim=1)
    # 计算注意力熵 — 熵越高说明模型对各词关注越分散，评语越模糊
    attn_for_entropy = attn_weights.squeeze(0).squeeze(1)[:original_len]
    attn_norm = attn_for_entropy / (attn_for_entropy.sum() + 1e-8)
    attn_entropy = float(-(attn_norm * torch.log(attn_norm + 1e-8)).sum())
    max_entropy = float(torch.log(torch.tensor(original_len, dtype=torch.float)))
    # 熵比：0=极度集中(清晰评价) 1=完全均匀(模糊评价)
    entropy_ratio = attn_entropy / (max_entropy + 1e-8)
    # 温度在 2.0 ~ 5.0 之间动态调节
    temperature = 2.0 + entropy_ratio * 3.0

    probs = F.softmax(output / temperature, dim=1)
    raw_neg = float(probs[0][0])
    raw_pos = float(probs[0][1])

    # 混合比例：把模型输出向 50% 拉，熵越高拉得越多
    blend = entropy_ratio * 0.7  # 最多拉 70% 向中间
    neg_prob = round(raw_neg * (1 - blend) + 0.5 * blend, 4)
    pos_prob = round(raw_pos * (1 - blend) + 0.5 * blend, 4)

    # 四档梯度标签
    if pos_prob > 0.65:
        sentiment = "强好评"
    elif pos_prob > 0.50:
        sentiment = "温和正面"
    elif pos_prob > 0.35:
        sentiment = "中性评价"
    else:
        sentiment = "差评"

    # 提取有效词的注意力权重（去掉填充部分），对有效词重新归一化使和为 1
    attn = attn_weights.squeeze(0).squeeze(1).cpu().numpy().tolist()
    attn = attn[:original_len]
    total = sum(attn)
    attn = [round(a / total, 4) for a in attn] if total > 0 else attn

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
