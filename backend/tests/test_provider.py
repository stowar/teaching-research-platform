# -*- coding: utf-8 -*-
"""test_provider.py — 多模型 provider 修复"""
from __future__ import annotations

import pytest
from backend.Agent.provider import get_ai_provider, IAIProvider
from backend.Agent.rules import DEFAULT_MODEL


class TestProviderMultiModel:
    """get_ai_provider 多模型支持"""

    def test_different_models_get_different_instances(self):
        """不同 model 参数应返回不同实例。"""
        a = get_ai_provider("model-a")
        b = get_ai_provider("model-b")
        assert a is not b
        assert a.model == "model-a"
        assert b.model == "model-b"

    def test_same_model_returns_cached_instance(self):
        """相同 model 参数应返回同一实例。"""
        a = get_ai_provider("model-x")
        b = get_ai_provider("model-x")
        assert a is b

    def test_default_model_used_when_none(self):
        """无参调用应使用 DEFAULT_MODEL。"""
        provider = get_ai_provider()
        assert provider.model == DEFAULT_MODEL

    def test_returns_iai_provider(self):
        """返回值应符合 IAIProvider 接口。"""
        provider = get_ai_provider("test")
        assert isinstance(provider, IAIProvider)
