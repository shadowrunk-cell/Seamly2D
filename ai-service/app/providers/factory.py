"""Фабрика провайдеров."""
from __future__ import annotations

from typing import Optional

from ..config import ProviderConfig, config as app_config
from .anthropic import AnthropicProvider
from .base import LLMProvider, ProviderError
from .openai_compat import OpenAICompatProvider

_PROVIDER_TYPES = {
    "openai_compat": OpenAICompatProvider,
    "anthropic": AnthropicProvider,
}


def create_provider(cfg: ProviderConfig) -> LLMProvider:
    """Создаёт экземпляр провайдера по его конфигурации."""
    cls = _PROVIDER_TYPES.get(cfg.type)
    if cls is None:
        raise ProviderError(f"Неизвестный тип провайдера: '{cfg.type}'")
    return cls(cfg)


def get_provider_for_role(role: str, provider_name: Optional[str] = None) -> LLMProvider:
    """Возвращает провайдера, который может обслуживать данную роль.

    Если указан provider_name — используем именно его и проверяем наличие роли.
    Иначе — первый подходящий провайдер.
    """
    if provider_name:
        for p in app_config.providers:
            if p.name == provider_name:
                if not p.has_role(role):
                    raise ProviderError(
                        f"Провайдер '{p.name}' не поддерживает роль '{role}'. "
                        f"Его роли: {[m.role for m in p.models]}"
                    )
                return create_provider(p)
        raise ProviderError(f"Провайдер '{provider_name}' не найден в providers.yaml")

    for p in app_config.providers:
        if p.has_role(role):
            return create_provider(p)

    raise ProviderError(
        f"Нет провайдера с ролью '{role}'. Проверьте providers.yaml — "
        f"настройте провайдера с ролью '{role}'."
    )
