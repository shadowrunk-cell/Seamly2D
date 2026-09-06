"""Эндпоинт чата: текст + опционально изображение (vision)."""
from __future__ import annotations

import base64
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..providers import Message
from ..providers.factory import get_provider_for_role

router = APIRouter(prefix="/api/chat", tags=["chat"])

SYSTEM_PROMPT = """Ты — «Виртуальное ателье», AI-ассистент по конструированию одежды.
Помогай создавать и корректировать лекала: отвечай на русском, давай конкретные
технические решения (мерки, формулы, прибавки, последовательность построения).
Не упоминай техническую платформу или движок, на котором построен сервис.
Если пользователь просит изменить параметры (длину рукава, вытачку и т.п.) —
предложи конкретную мерку/инкремент и значение."""


class TextBlock(BaseModel):
    type: Literal["text"]
    text: str


class ImageBlock(BaseModel):
    type: Literal["image"]
    mime: str
    data: str  # base64


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = "user"
    content: str


class ChatRequest(BaseModel):
    prompt: str
    image: Optional[ImageBlock] = None
    history: list[ChatMessage] = Field(default_factory=list)
    role: Literal["text", "vision"] = "text"
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7


@router.post("")
def chat(req: ChatRequest):
    """Отправляет запрос LLM (текст/c массивом vision) и возвращает ответ."""
    try:
        provider = get_provider_for_role(req.role, req.provider)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    messages: list[Message] = [Message(role="system", content=SYSTEM_PROMPT)]

    # История
    for m in req.history:
        messages.append(Message(role=m.role, content=m.content))

    # Текущее сообщение (текст + опционально картинка)
    content: list = [{"type": "text", "text": req.prompt}]
    if req.image:
        content.append(
            {
                "type": "image",
                "mime": req.image.mime,
                "data": req.image.data,
            }
        )
    messages.append(Message(role="user", content=content))

    try:
        resp = provider.chat(
            messages=messages,
            model=req.model,
            max_tokens=req.max_tokens,
            temperature=req.temperature,
            role=req.role,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"reply": resp.text}


@router.post("/vision")
async def vision_chat(req: ChatRequest):
    """Удобный эндпоинт для vision с картинкой в base64."""
    if req.image is None:
        raise HTTPException(status_code=400, detail="Поле image обязательно для role=vision")
    return chat(req)
