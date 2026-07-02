# -*- coding: utf-8 -*-
"""分层提示词组装器 — 替代 rules.py 中的巨型 build_system_prompt()"""
from __future__ import annotations

from backend.Agent.preprocessor import PreprocessResult
from backend.Agent.personality import Personality
from backend.Agent.achievements import ACHIEVEMENTS


def build_layered_prompt(
    preprocess: PreprocessResult,
    personality: Personality,
    user_name: str = "",
    user_state: dict = None,
) -> str:
    """组装分层系统提示词。

    Layer 1: 系统指令（行为规则，精简版）
    Layer 2: 状态层（personality status）
    Layer 3: 记忆层（RAG 检索结果）
    Layer 4: 预处理层（Call 2 优化上下文 + 工具结果）
    Layer 5: 用户状态（成就/配额/连续天数）

    上下文窗口（原始用户输入 + 历史消息）不在此 prompt 中，
    作为独立消息追加到 messages 数组，保证原样保留。
    """
    layers = [
        _build_system_layer(user_name),
        _build_state_layer(personality),
        _build_memory_layer(preprocess.retrieval_results),
        _build_preprocess_layer(preprocess),
        _build_user_state_layer(user_state),
    ]
    return "\n\n".join(l for l in layers if l)


# ── Layer 1: 系统指令 ──────────────────────────

def _build_system_layer(user_name: str) -> str:
    name_hint = f"当前对话的教师：{user_name}。" if user_name else ""
    return f"""你是 AI 教研助手，面向职业院校英语教师。给实际建议，不空谈理论。

{name_hint}

## 可用工具
- set_tone — 根据对话氛围切换语气（professional/casual/encouraging/analytical）
- check_memory — 查询历史记忆（补充检索）
- record_memory — 记住用户核心信息，记录偏好/研究方向/课程/班级等
- adjust_engagement — 根据对话质量调整投入度（delta: 正数增加，负数减少）
- adjust_attention — 根据话题一致性调整关注度（delta: 正数聚焦，负数发散）
- unlock_achievement — 授予教师教学成就（仅课堂场景类成就）

## 核心规则

### 一、投入度调整（每轮强制）
收到用户输入后必须判定互动维度，调用 adjust_engagement：
- 教师分享真实案例/课程细节/学生数据 → +5
- 教师追问细节/修改意见/深入探讨 → +3
- 教师表达认可/感谢 → +2
- 教师提出新需求/新话题 → +4
- 仅单字/表情/简短回应 → -3
- 表达不满/质疑 → -2

### 二、记忆使用
- 若上下文中提供了相关记忆，回复时引用并加上【根据你之前的信息……】
- 用户提供重要新信息时，调用 record_memory 记录

### 三、语气切换
根据对话氛围主动调用 set_tone：
- professional — 正式教学讨论、论文、政策话题
- encouraging — 教师表达困惑、焦虑、挫败时，温暖鼓励
- analytical — 深入分析、对比论证、数据讨论
- casual — 轻松闲聊、非正式交流
安全场景参照第四条。

### 四、输出规范
- Markdown 格式，核心信息加粗
- 基于已确认信息回复，不编造
- 全程中文回复

### 四、安全边界
检测暴力/违法/自残内容时：先确认是否为创作/讨论，再决定是否切换语气。"""


# ── Layer 2: 状态层 ────────────────────────────

def _build_state_layer(personality: Personality) -> str:
    return (
        f"## 当前助手状态\n"
        f"{personality.get_status()}\n"
        f"语气描述: {personality.get_tone_prompt()}"
    )


# ── Layer 3: 记忆层（RAG 检索结果）────────────

def _build_memory_layer(retrieval_results: list) -> str:
    if not retrieval_results:
        return "## 相关记忆\n无相关历史记忆。"

    lines = ["## 相关记忆（来自知识库检索）"]
    tier_labels = {"core": "核心", "reference": "参考", "peripheral": "边缘"}
    for m in retrieval_results[:8]:
        tier = m.get("tier", "")
        label = tier_labels.get(tier, tier)
        lines.append(f"- [{label}] {m['content']} ({m.get('created_at', '')})")
    return "\n".join(lines)


# ── Layer 4: 预处理层 ──────────────────────────

def _build_preprocess_layer(preprocess: PreprocessResult) -> str:
    parts = ["## 预处理上下文"]

    if preprocess.optimized_context:
        parts.append(preprocess.optimized_context)

    if preprocess.tool_results:
        parts.append("\n原始工具结果：")
        for name, result in preprocess.tool_results.items():
            parts.append(f"- {name}: {result}")

    return "\n".join(parts)


# ── Layer 5: 用户状态 ──────────────────────────

def _build_user_state_layer(user_state: dict = None) -> str:
    if not user_state:
        return ""

    parts = ["## 当前教师状态"]

    unlocked = user_state.get("unlocked_ach", [])
    total = user_state.get("total_ach", 0)
    if unlocked:
        names = "、".join(unlocked)
        parts.append(f"- 已解锁成就（{len(unlocked)}/{total}）：{names}")
    else:
        parts.append(f"- 尚未解锁任何成就（{total} 个待解锁）")

    msgs = user_state.get("messages_today", 0)
    limit = user_state.get("messages_limit", 30)
    if isinstance(limit, int):
        quota_left = max(0, limit - msgs)
        if quota_left <= 3:
            parts.append(f"- 今日配额紧张：仅剩 {quota_left} 条，请精简回复")
        else:
            parts.append(f"- 今日剩余配额：{quota_left} 条")

    streak = user_state.get("streak_days", 0)
    if streak >= 7:
        parts.append(f"- 连续活跃 {streak} 天 -- 铁杆用户")
    elif streak >= 3:
        parts.append(f"- 连续活跃 {streak} 天")

    mc = user_state.get("memory_count", 0)
    if mc >= 10:
        parts.append(f"- 已有 {mc} 条长期记忆")
    elif mc >= 3:
        parts.append(f"- 已有 {mc} 条长期记忆 -- 正在建立用户画像")

    if user_state.get("is_admin"):
        parts.append("- 该教师是平台管理员")

    return "\n".join(parts)


# ── 成就规则（从 rules.py 迁出）─────────────────

def build_achievement_rules(unlocked_ids: set = None) -> str:
    """生成成就授予规则，注入主模型 system prompt。"""
    unlocked = unlocked_ids or set()
    ai_judged = [a for a in ACHIEVEMENTS if a.get("ai_judged") and a["id"] not in unlocked]
    if not ai_judged:
        return "### 成就：所有 AI 判断成就已解锁。"

    lines = [
        "### 成就授予规则（AI 自主判断，每次对话最多授予 1 个）",
        "| 成就 ID | 名称 | 触发条件 |",
        "|---------|------|---------|",
    ]
    for ach in ai_judged:
        cond = ach.get("ai_hint", ach.get("desc", ""))
        lines.append(f"| {ach['id']} | {ach['name']} | {cond} |")
    return "\n".join(lines)
