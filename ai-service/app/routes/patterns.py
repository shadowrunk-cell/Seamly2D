"""Эндпоинты генерации паттернов (лекал)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse

from ..pattern.generator import build_vit, generate_pattern
from ..pattern.models import PatternRequest
from ..pattern.templates import TEMPLATES

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


@router.get("/templates")
def list_templates():
    """Список доступных шаблонов конструкций."""
    return {
        "templates": [
            {
                "key": t.key,
                "name": t.display_name,
                "description": t.description,
                "measurements_needed": t.required_measurements,
            }
            for t in TEMPLATES.values()
        ]
    }


@router.post("")
def create_pattern(req: PatternRequest):
    """Генерирует паттерн по шаблону и меркам пользователя."""
    try:
        result = generate_pattern(req)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result


@router.post("/download")
def download_pattern(req: PatternRequest):
    """Генерирует паттерн и возвращает его как файл .val."""
    result = generate_pattern(req)
    return PlainTextResponse(result.content, media_type="application/xml")


@router.get("/measurements/{template}")
def get_measurements_template(template: str):
    """Возвращает пример XML файла мерок для шаблона."""
    return PlainTextResponse(
        build_vit({}, template), media_type="application/xml"
    )
