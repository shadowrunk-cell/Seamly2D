"""Anthropic Claude провайдер (текст + зрение)."""
from __future__ import annotations

from typing import Optional

from anthropic import Anthropic
from anthropic.types import Message as ClaudeMessage

from .base import ChatResponse, LLMProvider, Message, ProviderError


class AnthropicProvider(LLMProvider):
    """Адаптер для Anthropic Messages API."""

    def __init__(self, config) -> None:
        super().__init__(config)
        api_key = config.get_api_key()
        if not api_key:
            raise ProviderError(
                f"Провайдер '{config.name}' (anthropic): не задан API-ключ "
                f"в переменной окружения '{config.api_key_env}'"
            )
        self._client = Anthropic(api_key=api_key)

    def supports_role(self, role: str) -> bool:
        return self.config.get_model_for_role(role) is not None

    def _resolve_model(self, role: str, model: Optional[str]) -> str:
        if model:
            return model
        m = self.config.get_model_for_role(role)
        if not m:
            raise ProviderError(f"Роль '{role}' не настроена у провайдера '{self.config.name}'")
        return m

    @staticmethod
    def _to_anthropic_messages(messages: list[Message]):
        """Конвертирует сообщения в формат Anthropic.

        Anthropic не принимает 'system' как роль — выносим системное сообщение отдельно.
        """
        system_parts: list[str] = []
        api_messages = []
        for msg in messages:
            if msg.role == "system":
                if isinstance(msg.content, str):
                    system_parts.append(msg.content)
                continue
            if isinstance(msg.content, str):
                api_messages.append({"role": msg.role, "content": msg.content})
                continue
            content = []
            for block in msg.content:
                if block.get("type") == "text":
                    content.append({"type": "text", "text": block.get("text", "")})
                elif block.get("type") == "image":
                    content.append(
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": block.get("mime", "image/png"),
                                "data": block.get("data"),
                            },
                        }
                    )
            api_messages.append({"role": msg.role, "content": content})
        return system_parts, api_messages

    def chat(
        self,
        messages: list[Message],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        role: str = "text",
    ) -> ChatResponse:
        model_name = self._resolve_model(role, model)
        system_parts, api_messages = self._to_anthropic_messages(messages)
        try:
            resp: ClaudeMessage = self._client.messages.create(
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system="\n\n".join(system_parts) or None,
                messages=api_messages,
            )
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Anthropic провайдер '{self.config.name}': {exc}") from exc

        text = "".join(b.text for b in resp.content if b.type == "text")
        return ChatResponse(text=text, raw=resp.model_dump())
