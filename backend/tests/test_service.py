# -*- coding: utf-8 -*-
"""test_service.py — chat() pipeline integration"""
from __future__ import annotations

import tempfile
from unittest.mock import patch, MagicMock

from backend.services.ai_chat.service import AIChatService


def _fake_message():
    m = MagicMock()
    m.role = "assistant"
    m.content = "reply text"
    m.timestamp = 1234567890
    return m


def _mock_chat():
    return {"role": "assistant", "content": "reply text", "tool_calls": []}


def _setup_db(mock_db):
    conv = MagicMock()
    conv.user_id = 1
    mock_db.count_user_messages_today.return_value = 0
    mock_db.get_conversation_by_id.return_value = conv
    mock_db.create_message.return_value = None
    mock_db.get_messages_by_conversation.return_value = [_fake_message()]
    mock_db.get_message_count.return_value = 1
    mock_db.touch_conversation.return_value = None


class TestChatPipeline:

    @patch("backend.services.ai_chat.pipeline.get_ai_provider")
    @patch("backend.services.ai_chat.service.ai_chat_db")
    def test_full_pipeline(self, mock_db, mock_provider):
        _setup_db(mock_db)
        mock_db.get_conversation_by_id.return_value = None
        mock_db.create_conversation.return_value = 1
        mock_provider.return_value.chat.return_value = _mock_chat()

        with tempfile.TemporaryDirectory() as d:
            with patch("backend.services.ai_chat.service.AI_DATA_DIR", d), \
                 patch("backend.services.ai_chat.achievements.AI_DATA_DIR", d):
                r = AIChatService().chat(1, "test message")

        assert r.msg == "回复成功"
        assert r.data.message.role == "assistant"
        assert r.data.state is not None
        assert r.data.conversation_id == 1

    @patch("backend.services.ai_chat.pipeline.get_ai_provider")
    @patch("backend.services.ai_chat.service.ai_chat_db")
    def test_pipeline_with_existing_conversation(self, mock_db, mock_provider):
        _setup_db(mock_db)
        mock_provider.return_value.chat.return_value = _mock_chat()

        with tempfile.TemporaryDirectory() as d:
            with patch("backend.services.ai_chat.service.AI_DATA_DIR", d), \
                 patch("backend.services.ai_chat.achievements.AI_DATA_DIR", d):
                r = AIChatService().chat(1, "follow-up", conversation_id=1)

        assert r.msg == "回复成功"
        assert r.data.conversation_id == 1


class TestChatQuota:

    @patch("backend.services.ai_chat.service.ai_chat_db")
    def test_over_quota_blocked(self, mock_db):
        mock_db.count_user_messages_today.return_value = 100
        r = AIChatService().chat(1, "hello")
        assert "已达上限" in r.data.message.content

    @patch("backend.services.ai_chat.pipeline.get_ai_provider")
    @patch("backend.services.ai_chat.service.ai_chat_db")
    def test_admin_bypass(self, mock_db, mock_provider):
        _setup_db(mock_db)
        mock_db.count_user_messages_today.return_value = 100
        mock_db.get_conversation_by_id.return_value = None
        mock_db.create_conversation.return_value = 1
        mock_provider.return_value.chat.return_value = _mock_chat()

        with tempfile.TemporaryDirectory() as d:
            with patch("backend.services.ai_chat.service.AI_DATA_DIR", d), \
                 patch("backend.services.ai_chat.achievements.AI_DATA_DIR", d):
                r = AIChatService().chat(1, "hello", role="admin")

        assert r.data.message.role == "assistant"
