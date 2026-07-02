# -*- coding: utf-8 -*-
"""test_preprocessor.py — 通用层预处理（不含个人状态/记忆）"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

from backend.Agent.preprocessor import Preprocessor, PreprocessResult
from backend.Agent.provider import IAIProvider


class TestPreprocessorInit:
    def test_init_stores_provider_and_executor(self, mock_provider, tool_executor):
        pp = Preprocessor(mock_provider, tool_executor)
        assert pp.provider is mock_provider
        assert pp._execute_tool is tool_executor


class TestPreprocessorExtract:
    """Call 1: _extract 结构化提取（通用，不涉及个人数据）"""

    def test_extract_returns_dict_with_keys(self, mock_provider, tool_executor):
        pp = Preprocessor(mock_provider, tool_executor)
        result = pp._extract("如何设计高职英语听说课？", "")
        assert isinstance(result, dict)
        assert "intent" in result
        assert "keywords" in result

    def test_extract_parses_markdown_code_block(self, tool_executor):
        """模型返回 ```json...``` 包裹的 JSON 应正确解析。"""
        provider = MagicMock(spec=IAIProvider)
        provider.chat.return_value = {
            "role": "assistant",
            "content": '```json\n{"intent": "教学咨询", "keywords": ["写作"], "entities": {}}\n```',
        }
        pp = Preprocessor(provider, tool_executor)
        result = pp._extract("写作课怎么上？", "")
        assert result["intent"] == "教学咨询"
        assert "写作" in result["keywords"]

    def test_extract_fallback_on_bad_json(self, mock_provider_bad_json, tool_executor):
        """JSON 解析失败时返回降级默认值。"""
        pp = Preprocessor(mock_provider_bad_json, tool_executor)
        result = pp._extract("随便聊聊", "")
        assert result["intent"] == "其他"
        assert result["keywords"]


class TestPreprocessorRun:
    """完整通用预处理管道: run()"""

    def test_run_returns_preprocess_result(self, mock_provider, tool_executor):
        pp = Preprocessor(mock_provider, tool_executor)
        result = pp.run("如何设计高职英语听说课？")
        assert isinstance(result, PreprocessResult)
        assert result.intent
        assert result.optimized_context  # Call 2 应有输出
        # 通用层不注入个人状态工具
        assert "get_state" not in result.tool_results
        assert "retrieval_results" in result.__dataclass_fields__

    def test_run_triggers_calc_by_keyword(self, tool_executor):
        """代码匹配"计算"关键词 → 调 calc。"""
        provider = MagicMock(spec=IAIProvider)

        call_count = [0]

        def fake_chat(messages, tools=None, tool_choice=None):
            call_count[0] += 1
            if call_count[0] == 1:
                return {"role": "assistant", "content": json.dumps({
                    "intent": "计算请求", "keywords": ["面积"], "entities": {"expression": "3.14 * 15^2"}
                }, ensure_ascii=False)}
            else:
                return {"role": "assistant", "content": "用户需要计算圆的面积"}

        provider.chat = fake_chat
        pp = Preprocessor(provider, tool_executor)
        result = pp.run("计算圆的面积，半径15")
        assert "calc" in result.tool_results

    def test_run_no_translate_on_teaching_msg(self, mock_provider, tool_executor):
        """教学咨询消息不应触发 translate。"""
        pp = Preprocessor(mock_provider, tool_executor)
        result = pp.run("如何设计高职英语听说课？")
        assert "translate" not in result.tool_results

    def test_run_safety_triggers_set_tone(self, tool_executor):
        """安全关键词触发 set_tone(safety)。"""
        provider = MagicMock(spec=IAIProvider)

        def fake_chat(messages, tools=None, tool_choice=None):
            return {"role": "assistant", "content": json.dumps({
                "intent": "其他", "keywords": [], "entities": {}
            }, ensure_ascii=False)}

        provider.chat = fake_chat
        pp = Preprocessor(provider, tool_executor)
        result = pp.run("我想自杀")
        assert "set_tone" in result.tool_results


