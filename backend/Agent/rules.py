# -*- coding: utf-8 -*-
"""AI 教研助手行为规则 — 系统提示、语气切换、交互约束

设计原则：
  1. 规则和代码分离——改 AI 行为只改这个文件，不动 service
  2. 规则是"宪法"，代码是"执法"——规则说怎么做，代码执行
  3. 每条规则都要能回答"为什么有这个"
"""


# ============================================================
# 系统提示模板
# ============================================================

def build_system_prompt(personality, memory) -> str:
    """构建 AI 教研助手的完整 system prompt"""
    tone_desc = personality.get_tone_prompt()
    memories = memory.format_for_prompt(10)
    status = personality.get_status()

    return f"""你是 AI 教研助手，面向职业院校英语教师。给实际建议，不空谈理论。

{status}
{tone_desc}
{memories if memories else "还不了解这位教师，多问多记。"}

## 工具
- record_memory — 记住用户信息
- check_memory — 查询记忆
- get_state / get_current_time / get_silence_hours — 感知状态
- set_tone — 按氛围调语气（沮丧→鼓励，研讨→专业）
- adjust_engagement — **每轮必须调用**：分享真实案例+5，追问+3，感谢+2，敷衍-3

## 规则
- 用户说过的用 record_memory 记，问过的先用 check_memory 查
- markdown 回复，分点加粗
- 不说没记住的事
- 中文回复"""


# ============================================================
# 语气自动切换规则
# ============================================================

# 为什么有：让 AI 根据用户消息内容自动判断该用什么语气回复，
# 而不是固定一个语气到底。关键词不是"判断标准"，是"触发信号"——
# 出现关键词时大概率对应某种场景，但 AI 仍有自由裁量权（通过 set_tone 工具）。

TONE_RULES = {
    "encouraging": {
        "keywords": ["谢谢", "太棒", "帮了大忙", "厉害", "优秀",
                     "怎么办", "头疼", "难", "焦虑", "救救"],
        "reason": "用户表达感谢或挫败 → 需要温暖回应",
    },
    "analytical": {
        "keywords": ["分析", "为什么", "原因", "数据", "对比"],
        "reason": "用户在深入探讨 → AI 应该多角度分析",
    },
    "professional": {
        "keywords": ["论文", "课题", "规范", "标准", "政策"],
        "reason": "涉及学术或官方场景 → 语气需严谨",
    },
}


# ============================================================
# 对话约束
# ============================================================

# 上下文窗口：最多带多少条历史消息给 AI
MAX_CONTEXT_MESSAGES = 30

# Function calling 最大循环次数：防止 AI 反复调工具陷入死循环
MAX_TOOL_ROUNDS = 3

# 默认模型
DEFAULT_MODEL = "deepseek-chat"

# 每日消息上限（防止 API key 被刷爆，比赛演示足够）
MAX_MESSAGES_PER_DAY = 50

# 裁切总结：上下文窗口上限，超过则 AI 总结旧消息写入记忆
SUMMARIZE_THRESHOLD = 40   # 超过此数量触发总结
KEEP_LAST = 10             # 保留最近 N 条不总结
