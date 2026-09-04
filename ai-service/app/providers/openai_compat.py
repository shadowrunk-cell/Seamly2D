"""OpenAI-совместимый провайдер.

Покрывает: OpenAI, Azure, Ollama, LM Studio, vLLM, GigaChat и большинство
локальных серверов — любой, кто реализует OpenAI chat-completions API.
"""
from __future__ import annotations

from typing import Optional

from openai import OpenAI

from .base import ChatResponse, LLMProvider, Message, ProviderError


class OpenAICompatProvider(LLMProvider):
    """Адаптер для OpenAI-совместимого API."""

    def __init__(self, config) -> None:
        super().__init__(config)
        api_key = config.get_api_key() or "not-needed"
        kwargs: dict = {"api_key": api_key}
        if config.base_url:
            kwargs["base_url"] = config.base_url
        self._client = OpenAI(**kwargs)

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
    def _to_openai_messages(messages: list[Message], vision: bool):
        """Конвертирует наши сообщения во формат OpenAI.

        Если vision=True и сообщение содержит картинки — собираем multimodal.
        """
        out = []
        for msg in messages:
            if isinstance(msg.content, str):
                out.append({"role": msg.role, "content": msg.content})
                continue

            content: list = []
            for block in msg.content:
                btype = block.get("type")
                if btype == "text":
                    content.append({"type": "text", "text": block.get("text", "")})
                elif btype == "image":
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{block.get('mime', 'image/png')};base64,{block.get('data')}"},
                        }
                    )
            out.append({"role": msg.role, "content": content})
        return out

    def chat(
        self,
        messages: list[Message],
        model: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        role: str = "text",
    ) -> ChatResponse:
        model_name = self._resolve_model(role, model)
        api_messages = self._to_openai_messages(messages, vision=(role == "vision"))
        try:
            resp = self._client.chat.completions.create(
                model=model_name,
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"OpenAI-совместимый провайдер '{self.config.name}': {exc}") from exc

        text = resp.choices[0].message.content or ""
        return ChatResponse(text=text, raw=resp.model_dump() if hasattr(resp, "model_dump") else {})
