# -*- coding: utf-8 -*-
"""AI Provider — OpenAI 兼容接口抽象"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from openai import OpenAI

from backend.core.config import settings


class IAIProvider(ABC):
    """AI 服务提供商接口"""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], tools: List[Dict] = None,
             tool_choice: str = "auto") -> Dict[str, Any]:
        """发送对话并返回回复"""
        ...


class OpenAICompatibleProvider(IAIProvider):
    """OpenAI 兼容 API（DeepSeek / 豆包 / OpenAI 通用）"""

    def __init__(self, api_key: str, base_url: str, model: str = "deepseek-v4-flash"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def chat(self, messages, tools=None, tool_choice="auto"):
        kwargs = dict(model=self.model, messages=messages)
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        response = self.client.chat.completions.create(**kwargs)
        msg = response.choices[0].message

        result = {"role": msg.role, "content": msg.content}
        if msg.tool_calls:
            result["tool_calls"] = [
                {"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                for tc in msg.tool_calls
            ]
        return result


# 全局单例，按配置决定用哪个 provider
_provider: IAIProvider = None


def get_ai_provider(model: str = None) -> IAIProvider:
    """获取 AI provider 实例"""
    global _provider
    if _provider is None:
        _provider = OpenAICompatibleProvider(
            api_key=settings.DOUBAO_API_KEY,
            base_url=getattr(settings, "AI_BASE_URL", "https://api.deepseek.com"),
            model=model or "deepseek-v4-flash",
        )
    return _provider
