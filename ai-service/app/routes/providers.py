"""Эндпоинты: список провайдеров и моделей."""
from __future__ import annotations

from fastapi import APIRouter

from ..config import config

router = APIRouter(prefix="/api/providers", tags=["providers"])


@router.get("")
def list_providers():
    """Возвращает список настроенных провайдеров и их модели по ролям."""
    result = []
    for p in config.providers:
        result.append(
            {
                "name": p.name,
                "type": p.type,
                "base_url": p.base_url,
                "models_by_role": {
                    role: p.get_model_for_role(role) for role in ("text", "vision")
                },
            }
        )
    return {"providers": result}
