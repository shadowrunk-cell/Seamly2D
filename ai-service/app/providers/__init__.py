"""Адаптеры LLM-провайдеров."""
from .base import LLMProvider, Message, ChatResponse, ProviderError
from .openai_compat import OpenAICompatProvider
from .anthropic import AnthropicProvider
from .factory import create_provider, get_provider_for_role

__all__ = [
    "LLMProvider",
    "Message",
    "ChatResponse",
    "ProviderError",
    "OpenAICompatProvider",
    "AnthropicProvider",
    "create_provider",
    "get_provider_for_role",
]
