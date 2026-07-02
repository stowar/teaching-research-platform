# -*- coding: utf-8 -*-
"""工具分类和路由 — 两阶段管道的工具分配"""

# Phase 1: 代码决定调用的工具（结果注入 prompt）
PREPROCESS_TOOL_NAMES = frozenset({
    "get_state",
    "get_current_time",
    "get_silence_timing",
    "calc",
    "translate",
})

# Phase 3: 主模型在 function calling 中自主调用的工具
MAIN_TOOL_NAMES = frozenset({
    "check_memory",
    "record_memory",
    "adjust_engagement",
    "adjust_attention",
    "unlock_achievement",
    "set_tone",
    # [TODO] "web_search",  # 暂不可用
})


def split_tool_definitions(all_tools: list) -> tuple:
    """将完整 TOOLS 列表拆分为 (preprocess_tools, main_tools)"""
    pre = [t for t in all_tools if t["function"]["name"] in PREPROCESS_TOOL_NAMES]
    main = [t for t in all_tools if t["function"]["name"] in MAIN_TOOL_NAMES]
    return pre, main
