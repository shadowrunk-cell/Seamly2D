"""Эндпоинты генерации паттернов (лекал)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import FileResponse, PlainTextResponse

from ..asyncq import download_path, get_job, submit_render_job
from ..pattern.generator import build_vit, generate_pattern
from ..pattern.models import PatternRequest
from ..pattern.render import (
    FORMATS,
    RenderError,
    RenderUnavailable,
    default_render_root,
    render_pattern,
)
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
def render_pattern_png(req: PatternRequest, format: str = "png"):
    """Генерирует лекало и рендерит его через headless Seamly2D (Docker).

    Формат: png (по умолчанию), svg, pdf, pdf-tiled, jpg, dxf, dxf-aama.
    """
    try:
        result = render_pattern(
            template_key=req.template,
            measurements=req.to_cm,
            size=req.size,
            adjustments=req.adjustments,
            out_dir=default_render_root() / "out",
            format=format,
        )
        media = FORMATS[result.format]["media"]
    except RenderUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RenderError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return FileResponse(
        result.file_path,
        media_type=media,
        filename=f"{req.template}_{req.size or 'custom'}.{result.format.replace('pdf-tiled', 'pdf')}",
    )


@router.post("/jobs")
def create_render_job(req: PatternRequest, format: str = "png"):
    """Ставит генерацию/рендер лекала в очередь и возвращает job_id (async)."""
    job_id = submit_render_job(
        template_key=req.template,
        measurements=req.to_cm,
        size=req.size,
        adjustments=req.adjustments,
        format=format,
    )
    job = get_job(job_id)
    return {"job_id": job_id, "status": job.state.lower()}


@router.get("/jobs/{job_id}")
def render_job_status(job_id: str, request: Request):
    """Статус асинхронной задачи (PENDING/STARTED/SUCCESS/FAILURE)."""
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return job.as_dict(request.headers.get("host") or "localhost")


@router.get("/jobs/{job_id}/result")
def render_job_result(job_id: str):
    """Скачать готовый файл результата асинхронной задачи."""
    from ..pattern.render import FORMATS

    path = download_path(job_id)
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="Результат ещё не готов или задача завершилась с ошибкой",
        )
    ext = path.suffix.lstrip(".").lower()
    media = "application/octet-stream"
    for fmt in FORMATS.values():
        if fmt["ext"] == ext:
            media = fmt["media"]
            break
    return FileResponse(path, media_type=media, filename=path.name)


@router.get("/measurements/{template}")
def get_measurements_template(template: str):
    """Возвращает пример XML файла мерок для шаблона."""
    return PlainTextResponse(
        build_vit({}, template), media_type="application/xml"
    )
