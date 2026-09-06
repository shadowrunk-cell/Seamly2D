"""Фасад асинхронных job-ов генерации лекал.

Использует Celery+Redis, а если брокер недоступен — локальный fallback
(фоновые потоки в рамках процесса). Это позволяет:
  * работать в dev/тестах без Redis;
  * на боевом окружении использовать полноценную очередь Celery.

Статусы совместимы с Celery: PENDING / STARTED / SUCCESS / FAILURE / RETRY.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from kombu.exceptions import OperationalError

from . import tasks
from .pattern.render import render_pattern
from .tasks import render_job

_LOCAL_JOBS: dict[str, dict[str, Any]] = {}
_LOCK = threading.Lock()


@dataclass
class JobSnapshot:
    job_id: str
    state: str
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None

    def as_dict(self, request_host: str) -> dict[str, Any]:
        """Представление для клиента (включая URL скачивания)."""
        data: dict[str, Any] = {
            "job_id": self.job_id,
            "status": self.state.lower(),
            "result": self.result,
            "error": self.error,
        }
        if self.state == "SUCCESS" and self.result:
            data["download_url"] = (
                f"http://{request_host}/api/patterns/jobs/{self.job_id}/result"
            )
        return data


def _broker_available() -> bool:
    """Проверяет доступность Redis (брокера Celery)."""
    try:
        from redis import from_url

        from .tasks import REDIS_URL

        redis = from_url(REDIS_URL, socket_connect_timeout=1)
        return bool(redis.ping())
    except Exception:  # noqa: BLE001
        return False


def submit_render_job(
    template_key: str,
    measurements: dict[str, float],
    size: str | None = None,
    adjustments: dict[str, float] | None = None,
    format: str = "png",
) -> str:
    """Ставит задачу рендера в очередь и возвращает job_id."""
    if _broker_available():
        try:
            async_result = render_job.delay(
                template_key,
                measurements,
                size,
                adjustments,
                format,
            )
            return async_result.id
        except OperationalError:
            pass  # брокер упал в момент вызова — fallback ниже

    # Локальный fallback: фоновая нить процесса.
    job_id = uuid.uuid4().hex
    with _LOCK:
        _LOCAL_JOBS[job_id] = {"state": "PENDING", "result": None, "error": None}

    def _work() -> None:
        with _LOCK:
            _LOCAL_JOBS[job_id]["state"] = "STARTED"
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
            payload = {
                "template": template_key,
                "size": size,
                "format": format,
                "file_path": str(result.file_path),
                "log": result.log,
            }
            with _LOCK:
                _LOCAL_JOBS[job_id] = {
                    "state": "SUCCESS",
                    "result": payload,
                    "error": None,
                }
        except Exception as exc:  # noqa: BLE001
            with _LOCK:
                _LOCAL_JOBS[job_id] = {
                    "state": "FAILURE",
                    "result": None,
                    "error": str(exc),
                }

    threading.Thread(target=_work, name=f"seamly-job-{job_id}", daemon=True).start()
    return job_id


def get_job(job_id: str) -> Optional[JobSnapshot]:
    """Возвращает снапшот задачи (или None, если задача неизвестна)."""
    if job_id in _LOCAL_JOBS:
        with _LOCK:
            entry = dict(_LOCAL_JOBS[job_id])
        return JobSnapshot(
            job_id=job_id,
            state=entry["state"],
            result=entry["result"],
            error=entry["error"],
        )

    try:
        async_result = tasks.celery_app.AsyncResult(job_id)
        state = async_result.state
    except Exception:  # noqa: BLE001 — Redis недоступен, к known локальному id это не относится
        return None
    if state == "SUCCESS":
        result = async_result.result if isinstance(async_result.result, dict) else None
        return JobSnapshot(job_id=job_id, state=state, result=result, error=None)
    if state == "FAILURE":
        error = None
        if async_result.result:
            try:
                error = str(async_result.result)
            except Exception:  # noqa: BLE001
                error = "Unknown failure"
        return JobSnapshot(job_id=job_id, state=state, result=None, error=error)
    return JobSnapshot(job_id=job_id, state=state, result=None, error=None)


def download_path(job_id: str) -> Optional[Path]:
    """Возвращает путь к готовому файлу результата, либо None."""
    job = get_job(job_id)
    if not job or job.state != "SUCCESS" or not job.result:
        return None
    rel = job.result.get("file_path") or job.result.get("png_path")
    if not rel:
        return None
    path = Path(rel)
    return path if path.exists() else None