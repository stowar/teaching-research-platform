# -*- coding: utf-8 -*-
"""
Sentiment Analysis Model: Embedding + Bi-GRU + Self-Attention
Adapted from Hotel_Emotion_Predict project.
"""
import torch
import torch.nn as nn


class SelfAttention(nn.Module):
    """自注意力层：学习每个词对情感分类的贡献权重"""

    def __init__(self, hidden_size):
        super(SelfAttention, self).__init__()
        self.hidden_size = hidden_size
        self.attention = nn.Linear(hidden_size, 1)

    def forward(self, gru_output):
        """
        :param gru_output: [batch_size, seq_len, hidden_size]
        :return: context_vector [batch_size, hidden_size], attn_weights [batch_size, seq_len, 1]
        """
        attn_scores = self.attention(gru_output)           # [B, L, 1]
        attn_weights = torch.softmax(attn_scores, dim=1)    # [B, L, 1]
        context_vector = torch.sum(gru_output * attn_weights, dim=1)  # [B, H]
        return context_vector, attn_weights


class SentimentGRU(nn.Module):
    """情感分类主模型"""

    def __init__(
        self,
        vocab_size,
        embedding_dim=128,
        hidden_size=256,
        num_layers=2,
        dropout=0.5,
        pad_idx=0
    ):
        super(SentimentGRU, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.embedding = nn.Embedding(
            num_embeddings=vocab_size,
            embedding_dim=embedding_dim,
            padding_idx=pad_idx
        )
        self.gru = nn.GRU(
            input_size=embedding_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        self.attention = SelfAttention(hidden_size)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 2)

    def forward(self, text):
        """
        :param text: [batch_size, seq_len]
        :return: output [batch_size, 2], attn_weights [batch_size, seq_len, 1]
        """
        embedded = self.embedding(text)              # [B, L, E]
        gru_output, _ = self.gru(embedded)           # [B, L, H]
        attn_vector, attn_weights = self.attention(gru_output)  # [B, H], [B, L, 1]
        dropped = self.dropout(attn_vector)
        output = self.fc(dropped)                    # [B, 2]
        return output, attn_weights
