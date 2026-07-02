# -*- coding: utf-8 -*-
"""测试夹具 — mock provider + 临时 memory/personality"""
from __future__ import annotations

import tempfile
import os
from unittest.mock import MagicMock

import pytest

from backend.Agent.provider import IAIProvider
from backend.Agent.memory import MemoryStore
from backend.Agent.personality import Personality


@pytest.fixture
def mock_provider():
    """返回模拟 IAIProvider，默认返回有效 JSON 提取结果。"""
    provider = MagicMock(spec=IAIProvider)
    provider.chat.return_value = {
        "role": "assistant",
        "content": (
            '{"intent": "教学咨询", "keywords": ["听说课", "教案"],'
            '"entities": {}}'
        ),
    }
    return provider


@pytest.fixture
def mock_provider_bad_json():
    """返回模拟 IAIProvider，返回非 JSON 内容，触发降级。"""
    provider = MagicMock(spec=IAIProvider)
    provider.chat.return_value = {
        "role": "assistant",
        "content": "这不是 JSON，只是随便说几句话",
    }
    return provider


@pytest.fixture
def temp_memory():
    """创建临时目录下的 MemoryStore，预填一条测试记忆。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = MemoryStore(999, tmpdir)
        store.add("用户是高职英语老师，教听说课", "preference")
        store.add("用户班级有 45 名学生", "experience")
        yield store


@pytest.fixture
def temp_personality():
    """创建默认 Personality 实例。"""
    return Personality("测试助手")


@pytest.fixture
def tool_executor():
    """模拟工具执行器，工具名和结果一一对应。"""
    def _execute(tool_name: str, **kwargs) -> str:
        results = {
            "get_state": "语气: professional | 投入度: 65/200 | 关注度: 42/100",
            "get_current_time": "2024-07-01 周一 14:30",
            "get_silence_timing": "用户 5 分钟前最后发言，处于短期静默",
            "calc": "3.14 * 15^2 = 706.5",
            "translate": "hello → 你好",
            "set_tone": "语气已切换为 professional",
        }
        return results.get(tool_name, f"{tool_name} 执行成功")
    return _execute
