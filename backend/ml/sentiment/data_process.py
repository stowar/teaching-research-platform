# -*- coding: utf-8 -*-
"""
数据预处理：jieba 分词、词典构建、文本标准化
"""
import re
import os
import jieba
import pandas as pd


def normalize_string(s):
    """文本标准化：去标点 → jieba 分词（与原始训练代码保持完全一致）"""
    if not s or not isinstance(s, str):
        return []
    # 删除标点符号与特殊字符，保留中文、英文、数字
    s = re.sub(r"[^\w\s一-鿿]", "", s)
    # jieba 分词
    word_list = jieba.lcut(s)
    return word_list


def get_dictionary(tsv_path):
    """
    从 TSV 文件构建词典
    :return: word2index, index2word
    """
    df = pd.read_csv(tsv_path, sep="\t", header=None, escapechar=None, engine="python")
    texts = df.iloc[:, 0].astype(str).tolist()
    labels = df.iloc[:, 1].tolist()
    pairs = [(normalize_string(t), y) for t, y in zip(texts, labels)]

    word2index = {"<PAD>": 0, "<UNK>": 1}
    word_n = 2
    for text, _ in pairs:
        for word in text:
            if word not in word2index:
                word2index[word] = word_n
                word_n += 1

    index2word = {v: k for k, v in word2index.items()}
    return pairs, word2index, index2word
