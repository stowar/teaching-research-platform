# -*- coding: utf-8 -*-
"""AI 聊天室数据访问层 — 裸 SQL，返回 DO"""
from __future__ import annotations

from backend.db.connection import execute_query, execute_one, execute_update, execute_insert
from backend.schema.do.ai_chat import ConversationDO, MessageDO


# ===================== 会话 =====================

def create_conversation(user_id: int, title: str = "新对话", model: str = "deepseek-chat") -> int:
    """创建新会话，返回 ID"""
    return execute_insert(
        "INSERT INTO conversations (user_id, title, model) VALUES (%s, %s, %s)",
        (user_id, title, model)
    )


def get_conversations_by_user(user_id: int) -> list[ConversationDO]:
    """获取用户所有会话（按更新时间倒序），含消息数"""
    sql = """
        SELECT c.*, COALESCE(m.msg_count, 0) AS msg_count
        FROM conversations c
        LEFT JOIN (
            SELECT conversation_id, COUNT(*) AS msg_count
            FROM messages
            GROUP BY conversation_id
        ) m ON c.id = m.conversation_id
        WHERE c.user_id = %s AND c.status = 1
        ORDER BY c.update_time DESC
    """
    rows = execute_query(sql, (user_id,))
    results = []
    for r in rows:
        do = ConversationDO.model_validate(r)
        do.msg_count = r.get("msg_count", 0)
        results.append(do)
    return results


def get_conversation_by_id(conversation_id: int) -> ConversationDO | None:
    """获取单个会话"""
    row = execute_one("SELECT * FROM conversations WHERE id = %s", (conversation_id,))
    return ConversationDO.model_validate(row) if row else None


def rename_conversation_db(conversation_id: int, title: str):
    """重命名会话"""
    execute_update("UPDATE conversations SET title = %s WHERE id = %s", (title, conversation_id))


def delete_conversation_db(conversation_id: int):
    """删除会话（级联删除消息由 MySQL FOREIGN KEY ON DELETE CASCADE 处理）"""
    execute_update("UPDATE conversations SET status = 0 WHERE id = %s", (conversation_id,))


def touch_conversation(conversation_id: int):
    """更新会话时间戳"""
    execute_update("UPDATE conversations SET update_time = NOW() WHERE id = %s", (conversation_id,))


# ===================== 消息 =====================

def create_message(conversation_id: int, role: str, content: str) -> int:
    """新增消息，返回 ID"""
    return execute_insert(
        "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
        (conversation_id, role, content)
    )


def get_messages_by_conversation(conversation_id: int) -> list[MessageDO]:
    """获取会话所有消息（按时间升序）"""
    rows = execute_query(
        "SELECT * FROM messages WHERE conversation_id = %s ORDER BY create_time ASC",
        (conversation_id,)
    )
    return [MessageDO.model_validate(r) for r in rows]


def get_message_count(conversation_id: int) -> int:
    """获取会话消息数"""
    row = execute_one(
        "SELECT COUNT(*) AS cnt FROM messages WHERE conversation_id = %s",
        (conversation_id,)
    )
    return row["cnt"] if row else 0
