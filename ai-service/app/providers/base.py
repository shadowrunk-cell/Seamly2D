"""Абстракция LLM-провайдера.

Единый интерфейс для всех провайдеров (OpenAI-совместимый, Anthropic и др.),
чтобы код сервиса не зависел от конкретной модели/провайдера.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Optional, Union

# Тип роли модели
ModelRole = Literal["text", "vision", "image"]

# Контентное сообщение: либо текст, либо текстовый блок + картинка
ContentBlock = dict


@dataclass
class Message:
    """Сообщение в чате."""

    role: Literal["system", "user", "assistant"]
    content: Union[str, list[ContentBlock]]


@dataclass
class ChatResponse:
    """Ответ модели."""

    text: str
    raw: dict = field(default_factory=dict)


class ProviderError(Exception):
    """Ошибка при обращении к провайдеру LLM."""


class LLMProvider(ABC):
    """Базовый класс провайдера LLM."""

    def __init__(self, config) -> None:
        self.config = config

    @abstractmethod
    def chat(
        self,
        messages: list[Message],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> ChatResponse:
        """Отправляет цепочку сообщений модели и возвращает ответ."""

    @abstractmethod
    def supports_role(self, role: ModelRole) -> bool:
        """Может ли провайдер обслуживать данную роль."""
