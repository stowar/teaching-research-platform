# -*- coding: utf-8 -*-
"""test_prompt_builder.py — 分层提示词组装"""
from __future__ import annotations

from backend.Agent.prompt_builder import (
    build_layered_prompt,
    build_achievement_rules,
    _build_system_layer,
    _build_state_layer,
    _build_memory_layer,
    _build_preprocess_layer,
    _build_user_state_layer,
)
from backend.Agent.preprocessor import PreprocessResult


class TestSystemLayer:
    def test_includes_core_instructions(self):
        result = _build_system_layer("张老师")
        assert "AI 教研助手" in result
        assert "张老师" in result
        assert "check_memory" in result
        assert "record_memory" in result
        assert "adjust_engagement" in result

    def test_no_user_name_works(self):
        result = _build_system_layer("")
        assert "当前对话的教师" not in result


class TestStateLayer:
    def test_includes_personality_status(self, temp_personality):
        result = _build_state_layer(temp_personality)
        assert "当前助手状态" in result
        assert "语气" in result


class TestMemoryLayer:
    def test_empty_retrieval(self):
        result = _build_memory_layer([])
        assert "无相关历史记忆" in result

    def test_with_retrieval_results(self):
        results = [
            {"content": "用户是数学老师", "tier": "core", "created_at": "2024-01-01"},
            {"content": "用户教听说课", "tier": "reference", "created_at": "2024-02-01"},
        ]
        result = _build_memory_layer(results)
        assert "数学老师" in result
        assert "听说课" in result
        assert "核心" in result
        assert "参考" in result


class TestPreprocessLayer:
    def test_includes_optimized_context(self):
        pre = PreprocessResult(
            optimized_context="用户想设计听说课教案，关注互动环节。",
            tool_results={"get_state": "投入度: 65", "get_current_time": "周一 14:30"},
        )
        result = _build_preprocess_layer(pre)
        assert "听说课" in result
        assert "投入度" in result

    def test_empty_preprocess(self):
        pre = PreprocessResult()
        result = _build_preprocess_layer(pre)
        assert "预处理上下文" in result


class TestUserStateLayer:
    def test_empty_state(self):
        result = _build_user_state_layer(None)
        assert result == ""

    def test_with_achievements(self):
        state = {
            "unlocked_ach": ["初次对话", "连续三天"],
            "total_ach": 10,
            "messages_today": 5,
            "messages_limit": 30,
            "streak_days": 7,
            "memory_count": 12,
        }
        result = _build_user_state_layer(state)
        assert "初次对话" in result
        assert "连续三天" in result
        assert "铁杆用户" in result

    def test_low_quota_warning(self):
        state = {"messages_today": 28, "messages_limit": 30}
        result = _build_user_state_layer(state)
        assert "配额紧张" in result


class TestBuildLayeredPrompt:
    def test_integrates_all_layers(self, temp_personality):
        pre = PreprocessResult(
            intent="教学咨询",
            keywords=["听说课"],
            retrieval_results=[{"content": "用户教英语", "tier": "core", "created_at": "2024-01-01"}],
            optimized_context="用户想设计高职英语听说课。",
        )
        result = build_layered_prompt(pre, temp_personality, "张老师")
        assert "AI 教研助手" in result           # Layer 1
        assert "当前助手状态" in result           # Layer 2
        assert "用户教英语" in result             # Layer 3
        assert "听说课" in result                # Layer 4


class TestAchievementRules:
    def test_includes_achievement_table(self):
        result = build_achievement_rules(set())
        assert "成就授予规则" in result or "成就" in result

    def test_all_unlocked_shows_complete(self):
        from backend.Agent.achievements import ACHIEVEMENTS
        all_ids = set(a["id"] for a in ACHIEVEMENTS if a.get("ai_judged"))
        result = build_achievement_rules(all_ids)
        assert "已解锁" in result
