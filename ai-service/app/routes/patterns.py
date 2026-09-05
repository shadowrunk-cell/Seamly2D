"""Эндпоинты генерации паттернов (лекал)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, PlainTextResponse

from ..pattern.generator import build_vit, generate_pattern
from ..pattern.models import PatternRequest
from ..pattern.render import RenderError, RenderUnavailable, render_pattern
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


@router.post("/render")
def render_pattern_png(req: PatternRequest):
    """Генерирует лекало и рендерит его в PNG через headless Seamly2D (Docker)."""
    import tempfile
    from pathlib import Path

    try:
        tmp_root = Path(tempfile.gettempdir())
        result = render_pattern(
            template_key=req.template,
            measurements=req.to_cm,
            size=req.size,
            adjustments=req.adjustments,
            out_dir=tmp_root / "seamly_render",
        )
    except RenderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RenderError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        result.png_path,
        media_type="image/png",
        filename=f"{req.template}_{req.size or 'custom'}.png",
    )


@router.get("/measurements/{template}")
def get_measurements_template(template: str):
    """Возвращает пример XML файла мерок для шаблона."""
    return PlainTextResponse(
        build_vit({}, template), media_type="application/xml"
    )
