"""Celery-приложение и задачи асинхронной генерации лекал.

Воркер запускается командой:

    celery -A app.tasks.celery_app worker --loglevel=info

URL брокера/бэкенда берётся из переменных окружения:
  SEAMLYAI_REDIS_URL (default `redis://localhost:6379/0`).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

from celery import Celery
from celery.exceptions import MaxRetriesExceededError

from .pattern.render import RenderError, render_pattern

log = logging.getLogger(__name__)

REDIS_URL = os.getenv("SEAMLYAI_REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "seamlyai",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_default_retry_delay=5,
    task_max_retries=3,
    broker_connection_retry_on_startup=True,
    result_expires=3600 * 24,  # результаты хранятся сутки
)


@celery_app.task(bind=True, name="patterns.render")
def render_job(
    self,
    template_key: str,
    measurements: dict[str, float],
    size: str | None,
    adjustments: dict[str, float] | None,
    format: str = "png",
) -> dict:
    """Рендерит лекало в файл (png/svg/pdf/dxf). Транзиентные сбои — ретрай с backoff.

    RenderError (например, пустая сцена) — терминальный FAILURE без ретрая.
    """
    try:
        result = render_pattern(
            template_key=template_key,
            measurements=measurements,
            size=size,
            adjustments=adjustments,
            out_dir=Path(__file__).resolve().parent.parent.parent.parent
            / "seamly-renderer"
            / "async_out",
            format=format,
        )
    except RenderError:
        raise
    except Exception as exc:  # noqa: BLE001 — транзиентный сбой (docker/сеть)
        try:
            raise self.retry(exc=exc) from exc
        except MaxRetriesExceededError:
            raise
    return {
        "template": template_key,
        "size": size,
        "format": format,
        "file_path": str(result.file_path),
        "log": result.log,
    }