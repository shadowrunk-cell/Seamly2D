"""Эндпоинты генерации паттернов (лекал)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import PlainTextResponse

from ..pattern.generator import build_vit, generate_pattern
from ..pattern.models import PatternRequest
from ..pattern.templates import GARMENT_CATEGORIES, GENDERS, TEMPLATES

router = APIRouter(prefix="/api/patterns", tags=["patterns"])


@router.get("/templates")
def list_templates(
    category: Optional[str] = None,
    gender: Optional[str] = None,
):
    """Каталог доступных изделий (шаблонов) с фильтрами по виду и полу."""
    items = [
        {
            "key": t.key,
            "name": t.display_name,
            "description": t.description,
            "category": t.category,
            "gender": t.gender,
            "image": t.image,
            "measurements_needed": t.required_measurements,
        }
        for t in TEMPLATES.values()
    ]
    if category:
        items = [i for i in items if i["category"] == category]
    if gender:
        items = [i for i in items if i["gender"] == gender]

    return {
        "categories": GARMENT_CATEGORIES,
        "genders": GENDERS,
        "templates": items,
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
