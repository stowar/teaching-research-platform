# -*- coding: utf-8 -*-
"""
Sentiment Predictor — 情感分析推理引擎
========================================
架构：BiGRU + Self-Attention 神经网络 + 六层温度缩放后处理

设计原则：
  1. 神经网络负责"理解"文本，给出原始得分
  2. 后处理负责"校准"置信度——让模型该确定时确定，该犹豫时犹豫
  3. 规则兜底覆盖神经网络的盲区（短文本、OOV、转折句）

温度体系（六个层级，按优先级排列）：
  L1 — 短文本规则：≤3 词直接走关键词匹配，不经过网络
  L2 — 注意力熵检测：熵高 = 关注分散 = 评语模糊，升温趋向 50%
  L3 — 原始置信度门控：模型自己确定时（>80%/<20%）降温保护强信号
  L4 — 中性词强制高温：检测到"还行/一般/吧"等中性词，不盲信模型
  L5 — 转折词强制高温：检测到"但/只是/不过"等转折词，保护被前件带偏的模型
  L6 — 极端词降温：检测到"太棒/超级/恶心/极其"等，让强情绪穿透
"""

import os
import json
import threading
import torch
import torch.nn.functional as F

from backend.ml.sentiment.model import SentimentGRU
from backend.ml.sentiment.data_process import normalize_string
from backend.core.config import settings

# ============================================================
# 全局单例：模型和词典只加载一次，所有请求共享
# ============================================================
_model = None       # SentimentGRU 实例
_word2index = None  # 词→索引 映射表
_index2word = None  # 索引→词 映射表（保留，未使用）
_lock = threading.Lock()  # 双重检查锁，保证线程安全

# ============================================================
# 路径与模型常量（与训练时保持一致）
# ============================================================
ASSETS_DIR = os.path.join(settings.BASE_DIR, "backend", "ml", "sentiment", "assets")
MODEL_PATH = os.path.join(ASSETS_DIR, "model.pt")
WORD2INDEX_PATH = os.path.join(ASSETS_DIR, "word2index.json")

MAX_SEQ_LEN = 50        # 最大序列长度，超过截断，不足补零
EMBEDDING_DIM = 128     # 词向量维度
HIDDEN_SIZE = 256       # GRU 隐藏层大小
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _load_model():
    """
    懒加载模型（首次调用时加载，后续直接从内存取）
    使用双重检查锁保证线程安全：
      - 外层 if：避免每次调用都竞争锁（已加载后直接返回）
      - 内层 if：避免两个线程同时通过外层 if 后重复加载
    """
    global _model, _word2index, _index2word

    # 快速路径：已加载直接返回（无锁，高性能）
    if _model is not None:
        return _model, _word2index, _index2word

    with _lock:
        # 双重检查：可能另一个线程已在我们等锁期间加载完毕
        if _model is not None:
            return _model, _word2index, _index2word

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(f"模型文件不存在: {MODEL_PATH}")
        if not os.path.exists(WORD2INDEX_PATH):
            raise RuntimeError(f"词典文件不存在: {WORD2INDEX_PATH}")

        # 加载词典（训练时保存的 JSON，保证与模型 vocab_size 一致）
        with open(WORD2INDEX_PATH, "r", encoding="utf-8") as f:
            _word2index = json.load(f)

        # 初始化模型结构，参数必须与训练时完全一致
        vocab_size = len(_word2index)
        model = SentimentGRU(
            vocab_size=vocab_size,
            embedding_dim=EMBEDDING_DIM,
            hidden_size=HIDDEN_SIZE,
            num_layers=2,
            dropout=0.5,
            pad_idx=0
        )

        # 加载训练好的权重
        state_dict = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
        model.load_state_dict(state_dict)
        model.to(DEVICE)
        model.eval()  # 冻结 dropout / batch norm

        _model = model
        return _model, _word2index, _index2word


def predict(text: str):
    """
    单条文本情感预测

    处理流程：
      1. 文本预处理（jieba 分词）
      2. [L1] 短文本规则兜底（≤3 词）
      3. 词→索引→填充→张量化
      4. 神经网络前向传播
      5. [L2-L6] 六层温度缩放后处理
      6. 四档梯度标签输出

    Args:
        text: 输入文本（中文）

    Returns:
        dict: {
            sentiment:    str   — 四档标签（强好评/温和正面/中性评价/差评）
            pos_prob:     float — 正面概率 [0, 1]
            neg_prob:     float — 负面概率 [0, 1]
            words:        list  — 分词后词列表
            attn_weights: list  — 每个词的注意力权重（归一化和=1）
        }
    """
    # ============================================================
    # 第一步：文本预处理
    # ============================================================
    model, word2index, index2word = _load_model()
    words = normalize_string(text)

    # ============================================================
    # L1 — 短文本规则兜底
    # ============================================================
    # 背景：神经网络输入固定 50 位，≤3 个词的文本有 47+ 位是 padding。
    #       BiGRU 在大量 padding 上信号极弱，单字"好"被误判为负面的根因在此。
    # 方案：≤3 词直接走关键词匹配，不经过网络。
    #
    # 置信度分两级：
    #   95% — 强信号词（"好/差/烂/赞"），语义极其明确，不需要上下文
    #   65% — 弱信号词（"还行/挺好/不好"），需要上下文才能完全确定
    #
    # 额外用原始文本（未分词）兜底：jieba 可能把"还行"切成"还"+"行"两个单字，
    #   "还"和"行"都不是关键词 → 分数为 0 → 误判中性。原始文本"还行"能命中弱正面词。
    if words and len(words) <= 3:
        raw_text = text.replace(' ', '').strip()  # 去除空格，保留原始文本

        # ---- 强信号词：单字/双字，含义极其明确 → 95% 置信 ----
        strong_pos = {'好','很好','棒','赞','优秀','不错','认真','用心','负责','专业','值得','推荐','喜欢'}
        strong_neg = {'差','差评','差劲','烂','糟糕','垃圾','水','糊弄','敷衍','无聊','失望','无语','枯燥','别选'}

        # ---- 弱信号词：偏正面/负面，但需要上下文才能完全确定 → 65% 置信 ----
        weak_pos = {'还行','还可以','可以','挺好','满意','给力','靠谱','有趣','学到了'}
        weak_neg = {'不好','不行','不怎么样','没意思','没劲','不值','后悔','浪费时间','听不懂'}

        # 遍历分词结果 + 原始文本，统计正/负信号
        score = 0
        is_strong = False
        for w in words + [raw_text]:
            if w in strong_pos:
                score += 1
                is_strong = True
            elif w in strong_neg:
                score -= 1
                is_strong = True
            elif w in weak_pos:
                score += 1
            elif w in weak_neg:
                score -= 1

        # 根据信号强度和方向输出概率
        conf = 0.95 if is_strong else 0.65
        if score > 0:
            pos_prob, neg_prob = conf, round(1 - conf, 4)
        elif score < 0:
            pos_prob, neg_prob = round(1 - conf, 4), conf
        else:
            pos_prob = neg_prob = 0.50  # 无任何信号 → 纯中性

        # 四档标签映射
        if pos_prob > 0.65: sentiment = "强好评"
        elif pos_prob > 0.50: sentiment = "温和正面"
        elif pos_prob > 0.35: sentiment = "中性评价"
        else: sentiment = "差评"

        return {
            "sentiment": sentiment,
            "pos_prob": pos_prob,
            "neg_prob": neg_prob,
            "words": words,
            "attn_weights": [1.0 / len(words)] * len(words)  # 规则模式下均匀分配
        }

    # ============================================================
    # 第二步：空文本处理
    # ============================================================
    if not words:
        return {
            "sentiment": "无法判断",
            "pos_prob": 0.0,
            "neg_prob": 0.0,
            "words": [],
            "attn_weights": []
        }

    # ============================================================
    # 第三步：文本 → 张量
    # ============================================================
    # 词转索引，词典中不存在的词映射为 1（<UNK>）
    x = [word2index.get(word, 1) for word in words]

    # 截断：超过 50 词的文本只保留前 50 词
    if len(x) > MAX_SEQ_LEN:
        x = x[:MAX_SEQ_LEN]
        words = words[:MAX_SEQ_LEN]
    original_len = len(x)  # 记录有效词数（后续去掉 padding 用）

    # 填充：不足 50 位用 0（<PAD>）补齐
    x += [0] * (MAX_SEQ_LEN - len(x))

    # 转为 (1, 50) 的 batch 张量
    tensor_x = torch.tensor(x, dtype=torch.long, device=DEVICE).unsqueeze(0)

    # ============================================================
    # 第四步：神经网络前向传播
    # ============================================================
    with torch.no_grad():
        output, attn_weights = model(tensor_x)
    # output.shape = (1, 2)        — [负向得分, 正向得分]
    # attn_weights.shape = (1, 50) — 每个位置的注意力权重

    # ============================================================
    # 第五步：温度缩放后处理（L2-L6）
    # ============================================================
    # 以下每一层都在回答同一个问题：
    #   "模型给的分数，我们该信多少？"
    #
    # 核心变量：
    #   temperature  — 越高概率越趋向 50/50（软化 softmax）
    #   blend        — 越高结果越趋向 50/50（线性混合）
    #
    # 核心公式：
    #   final_prob = raw_prob * (1 - blend) + 0.5 * blend
    #   → blend=0   : 完全信任模型
    #   → blend=0.7 : 模型输出被拉向 50% 约 70%
    #   → blend=1.0 : 完全忽略模型，输出 50/50

    # ---- L2: 注意力熵计算 ----
    # 熵衡量注意力分布的均匀程度：
    #   熵低 = 模型紧盯着少数词 → 信号清晰 → 可以信任
    #   熵高 = 模型关注分散在所有词 → 信号模糊 → 需要降温
    #
    # 只计算有效词（去掉 padding 部分），避免 padding 稀释熵值
    raw_probs = F.softmax(output, dim=1)                        # 原始 softmax（温度=1）
    attn_for_entropy = attn_weights.squeeze(0).squeeze(1)[:original_len]
    attn_norm = attn_for_entropy / (attn_for_entropy.sum() + 1e-8)  # 归一化
    attn_entropy = float(-(attn_norm * torch.log(attn_norm + 1e-8)).sum())
    max_entropy = float(torch.log(torch.tensor(original_len, dtype=torch.float)))
    # 熵比：0 = 极度集中（清晰评价） → 1 = 完全均匀（模糊评价）
    entropy_ratio = attn_entropy / (max_entropy + 1e-8)

    # ---- L6: 极端情绪词检测 ----
    # 背景：强烈情绪词（"太棒了""恶心"）是明确的信号，应让模型高置信度输出。
    #       V1 时期统一高温把所有输出压到 55%，强情绪也被误压了。
    # 方案：极端词出现时，温度降至接近 1.0 + 极少混合，保留模型的强判断。
    # 注意：此检测必须在温度选择之前，因为极端词优先级最高。
    extreme_kw = {
        '太棒','超级','无敌','绝了','完美','爱死','令人发指','恶心','极其','避雷',
        '全校最','史上最','这辈子最','受不了','想吐','崩溃','疯了','救命','天哪',
        '从来没有','无可挑剔','不可思议','惊艳','震撼','炸裂'
    }
    has_extreme = any(kw in text for kw in extreme_kw)

    # ---- L3: 原始置信度门控 ----
    # 问题：V1/V2 时期，温度在 softmax 之前就已设定，用的是固定公式。
    #       长全正面评语熵高 → 自动升温 → 信号被碾。但模型其实很确定（pos=89.75%）。
    # 方案：先用无温度 softmax 试判模型是否确定。
    #       raw_pos > 80% 或 < 20% → 模型很确定 → 降温保护
    #       35%-65%                  → 模型不确定 → 升温趋向 50%
    #       中间地带                  → 线性插值平滑过渡
    probs_raw = F.softmax(output, dim=1)  # 重复了 raw_probs，但逻辑上独立
    prey_raw_pos = float(probs_raw[0][1])

    # ---- L4: 中性词检测 ----
    # 问题："勉强还行吧不好不坏" 被模型判为 83% 正面。模型错了但低温保护了错误。
    # 方案：检测到"还行/一般/吧/不好不坏/勉强/凑合"等中性词 →
    #       强制高温高混（3.0+ / 0.8），因为中性词出现意味着评语本质上就是模糊的。
    neutral_kw = {
        '还行','一般','吧','普通','差不多','就那样','还行吧','不好不坏',
        '勉强','凑合','马马虎虎','说得过去','过得去','中规中矩','平平'
    }
    has_neutral_kw = any(kw in text for kw in neutral_kw)

    # ---- L5: 转折词检测 ----
    # 问题："讲课通俗易懂，但节奏偏快跟不上" 被模型判为 92% 正面。
    #       BiGRU 按顺序读取，前半句正面词的注意力天然压倒后半句负面词。
    #       这是架构层面的局限——RNN 不具备真正的"转折"建模能力。
    # 方案：检测到"但/只是/不过/然而/虽说/虽然/可惜"等转折词 →
    #       强制高温高混（与中性词同等处理），因为转折本身就意味着前面的判断需要打折扣。
    #       这不是架构解法，是实用主义妥协。
    contrast_kw = {
        '但','但是','只是','不过','然而','可惜','遗憾的是','问题是','缺点是','不足的是',
        '可','却','偏偏','无奈','没想到','哪知','哪知道','谁知','谁知道',
        '遗憾的是','叫人失望的是','不太好的是','需要改进的是','不够好的是',
        '虽说','虽然','尽管','就算','哪怕','固然','即使'
    }
    has_contrast = any(kw in text for kw in contrast_kw)

    # ---- 温度与混合系数决策树 ----
    # 优先级：极端词 > 转折词/中性词 > 模型确定 > 模型不确定
    if has_extreme:
        # L6: 极端情绪 → 几乎不降，让模型放手判断
        temperature = 1.0 + entropy_ratio * 0.5
        max_blend = 0.0
    elif has_neutral_kw or has_contrast:
        # L4 + L5: 中性/转折 → 强制高温高混，趋向 50%
        temperature = 3.0 + entropy_ratio * 2.5
        max_blend = 0.8
    elif prey_raw_pos > 0.80 or prey_raw_pos < 0.20:
        # L3-高置信: 模型很确定 → 低温低混，信任模型
        temperature = 1.2 + entropy_ratio * 1.0
        max_blend = 0.1
    elif 0.35 < prey_raw_pos < 0.65:
        # L3-低置信: 模型不确定 → 高温高混，趋向 50%
        temperature = 2.0 + entropy_ratio * 3.0
        max_blend = 0.7
    else:
        # L3-中间地带: 模型 65%-80% / 20%-35% 确定度 → 线性插值
        t = min(1.0, abs(prey_raw_pos - 0.5) / 0.3)
        temperature = (2.0 + entropy_ratio * 3.0) * (1 - t) + (1.2 + entropy_ratio * 1.0) * t
        max_blend = max(0.1, 0.7 * (1 - t) + 0.1 * t)

    # ---- 应用温度缩放 ----
    probs = F.softmax(output / temperature, dim=1)
    raw_neg = float(probs[0][0])
    raw_pos = float(probs[0][1])
    raw_conf = abs(raw_pos - raw_neg)  # 温度缩放后的确定度

    # ---- 混合策略 ----
    # 公式：final = raw * (1 - blend) + 0.5 * blend
    # 含义：把模型输出向 50/50 拉 blend 比例
    # 双重约束：
    #   1. entropy_ratio * max_blend  — 熵越高拉得越多
    #   2. (1 - raw_conf) * 0.85      — 模型越不确定拉得越多
    #   取两者中较小值，避免过度混合
    blend = min(entropy_ratio * max_blend, (1 - raw_conf) * 0.85)
    neg_prob = round(raw_neg * (1 - blend) + 0.5 * blend, 4)
    pos_prob = round(raw_pos * (1 - blend) + 0.5 * blend, 4)

    # ============================================================
    # 第六步：四档梯度标签
    # ============================================================
    # 将连续概率映射为离散标签，阈值来自对教学评价场景的理解：
    #   > 65%  → 强好评       : 明显正面，可以放心采纳
    #   50-65% → 温和正面     : 偏正面但有保留/中性偏正面
    #   35-50% → 中性评价     : 模糊/混合/转折，不下定论
    #   < 35%  → 差评         : 明显负面
    if pos_prob > 0.65:
        sentiment = "强好评"
    elif pos_prob > 0.50:
        sentiment = "温和正面"
    elif pos_prob > 0.35:
        sentiment = "中性评价"
    else:
        sentiment = "差评"

    # ============================================================
    # 第七步：注意力权重处理
    # ============================================================
    # 只取有效词（去掉 padding 位置）
    # 对有效词重新归一化：使权重和为 1，每个词显示的是它占有效词的百分比
    #   → 6 个词时每个平均 ~17%，比原始值（1.7%）直观得多
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
    """检查模型文件与词典是否就绪"""
    return os.path.exists(MODEL_PATH) and os.path.exists(WORD2INDEX_PATH)
