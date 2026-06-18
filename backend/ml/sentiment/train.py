# -*- coding: utf-8 -*-
"""
训练情感分析模型
使用 teaching-research-platform 的 train.tsv 数据，训练 Embedding + BiGRU + Attention
"""
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import torch, torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from model import SentimentGRU
from data_process import normalize_string

# ============ 路径 ============
ASSETS = os.path.join(os.path.dirname(__file__), "assets")
TRAIN_FILE = os.path.join(ASSETS, "train.tsv")
MODEL_PATH = os.path.join(ASSETS, "model.pt")
WORD2INDEX_PATH = os.path.join(ASSETS, "word2index.json")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ============ 超参数 ============
MAX_SEQ_LEN = 50
EMBEDDING_DIM = 128
HIDDEN_SIZE = 256
NUM_LAYERS = 2
DROPOUT = 0.5
LEARNING_RATE = 2e-4
EPOCHS = 10
BATCH_SIZE = 16

# ============ 1. 加载数据 ============
print(f"[1/5] 加载数据: {TRAIN_FILE} (device={DEVICE})")
pairs = []
with open(TRAIN_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        parts = line.rsplit("\t", 1)
        if len(parts) != 2:
            continue
        text, label = parts[0], int(parts[1])
        words = normalize_string(text)
        if words:
            pairs.append((words, label))

print(f"  有效样本: {len(pairs)}")

# ============ 2. 构建词典 ============
print("[2/5] 构建词典...")
word2index = {"<PAD>": 0, "<UNK>": 1}
for words, _ in pairs:
    for w in words:
        if w not in word2index:
            word2index[w] = len(word2index)

vocab_size = len(word2index)
print(f"  词典大小: {vocab_size}")

# 保存词典
with open(WORD2INDEX_PATH, "w", encoding="utf-8") as f:
    json.dump(word2index, f, ensure_ascii=False)
print(f"  词典已保存: {WORD2INDEX_PATH}")

# ============ 3. Dataset ============
class SeqDataset(Dataset):
    def __init__(self, pairs, word2index, max_len):
        self.pairs = pairs
        self.word2index = word2index
        self.max_len = max_len

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        words, label = self.pairs[idx]
        x = [self.word2index.get(w, 1) for w in words]
        x = x[:self.max_len] + [0] * (self.max_len - len(x))
        return torch.tensor(x, dtype=torch.long), torch.tensor(label, dtype=torch.long)

dataset = SeqDataset(pairs, word2index, MAX_SEQ_LEN)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# ============ 4. 训练 ============
print(f"[3/5] 初始化模型 (vocab={vocab_size}, emb={EMBEDDING_DIM}, hidden={HIDDEN_SIZE})...")
model = SentimentGRU(vocab_size, EMBEDDING_DIM, HIDDEN_SIZE, NUM_LAYERS, DROPOUT, pad_idx=0)
model.to(DEVICE)
model.train()

optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
criterion = nn.CrossEntropyLoss()

print(f"[4/5] 开始训练 ({EPOCHS} 轮, batch={BATCH_SIZE})...")
start = time.time()

for epoch in range(EPOCHS):
    total_loss = 0.0
    total_correct = 0
    total_samples = 0

    for x, y in dataloader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        output, _ = model(x)
        loss = criterion(output, y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = output.argmax(dim=1)
        total_correct += (pred == y).sum().item()
        total_samples += y.size(0)

    avg_loss = total_loss / len(dataloader)
    acc = total_correct / total_samples
    elapsed = time.time() - start
    print(f"  Epoch {epoch+1:2d}/{EPOCHS} | loss={avg_loss:.4f} | acc={acc:.2%} | {elapsed:.0f}s")

# ============ 5. 保存模型 ============
print(f"[5/5] 保存模型: {MODEL_PATH}")
torch.save(model.state_dict(), MODEL_PATH)
print(f"  完成! 训练耗时 {time.time()-start:.0f}s")
