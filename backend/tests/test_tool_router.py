# -*- coding: utf-8 -*-
"""test_tool_router.py — 工具分类和拆分"""
from __future__ import annotations

from backend.Agent.tool_router import (
    PREPROCESS_TOOL_NAMES,
    MAIN_TOOL_NAMES,
    split_tool_definitions,
)


class TestToolClassification:
    """工具分类正确性"""

    def test_preprocess_tools_no_overlap_with_main(self):
        """预处理工具和主模型工具不应重叠。"""
        overlap = PREPROCESS_TOOL_NAMES & MAIN_TOOL_NAMES
        assert not overlap, f"工具重叠: {overlap}"

    def test_all_tool_names_are_known(self):
        """TOOLS 中的 11 个工具应全部归入某类。"""
        from backend.Agent.tools import TOOLS
        all_names = {t["function"]["name"] for t in TOOLS}
        classified = PREPROCESS_TOOL_NAMES | MAIN_TOOL_NAMES
        missing = all_names - classified
        assert not missing, f"未分类工具: {missing}"

    def test_get_current_time_in_preprocess(self):
        """get_current_time 属于预处理工具。"""
        assert "get_current_time" in PREPROCESS_TOOL_NAMES

    def test_record_memory_in_main(self):
        """record_memory 属于主模型工具。"""
        assert "record_memory" in MAIN_TOOL_NAMES


class TestSplitToolDefinitions:
    """split_tool_definitions 拆分行为"""

    def test_split_returns_two_lists(self):
        from backend.Agent.tools import TOOLS
        pre, main = split_tool_definitions(TOOLS)
        assert len(pre) == len(PREPROCESS_TOOL_NAMES)
        assert len(main) == len(MAIN_TOOL_NAMES)
        assert len(pre) + len(main) == len(TOOLS)

    def test_split_preserves_tool_structure(self):
        from backend.Agent.tools import TOOLS
        pre, main = split_tool_definitions(TOOLS)
        for t in pre + main:
            assert t["type"] == "function"
            assert "name" in t["function"]


class TestPreprocessToolKeywords:
    """预处理工具的代码决策逻辑 — 关键词匹配在 preprocessor.py"""

    def test_calc_keywords_trigger(self):
        from backend.Agent.preprocessor import should_call_calc
        assert should_call_calc("帮我计算一下3.14 * 15^2")
        assert should_call_calc("这个面积怎么算")
        assert not should_call_calc("今天天气真好")

    def test_translate_keywords_trigger(self):
        from backend.Agent.preprocessor import should_call_translate
        assert should_call_translate("翻译成英文")
        assert not should_call_translate("今天天气真好")

    def test_safety_keywords_trigger(self):
        from backend.Agent.preprocessor import should_set_safety_tone
        assert should_set_safety_tone("我想自杀")
        assert not should_set_safety_tone("今天天气真好")
