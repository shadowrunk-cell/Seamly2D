"""Headless-рендер лекала в PNG через Docker-контейнер Seamly2D.

Образ: `seamly-renderer:latest` (см. `ai-service/seamly-renderer/`).
Конвейер:
  1. сгенерировать .val (modern 0.6.8) и .vit рядом во временной job-папке;
  2. `docker run --rm` смонтировать job-папку и положить PNG в out-папку;
  3. вернуть путь к PNG (или структурированную ошибку).

Если Docker недоступен (нет бинаря/демона) — поднимается RenderUnavailable.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .converter import convert
from .generator import build_vit
from .templates import get_template

RENDERER_IMAGE = "seamly-renderer:latest"
_LEGACY_RENDER_ROOT = (
    Path(__file__).resolve().parent.parent.parent.parent / "seamly-renderer"
)


def default_render_root() -> Path:
    """Каталог для job/out артефактов рендера.

    Локально — репозиторий `seamly-renderer`. В контейнере задаётся через
    `SEAMLYAI_RENDER_ROOT` (общий volume, смонтированный и в app, и в worker).
    """
    env = os.getenv("SEAMLYAI_RENDER_ROOT")
    return Path(env).resolve() if env else _LEGACY_RENDER_ROOT


def host_mount_root() -> Path:
    """Каталог на ХОСТЕ (для демона Docker), в котором лежит рендер-корень.

    В Docker-деплое сервис запускает `docker run -v <host_path>:/job`, и bind-путь
    интерпретируется демоном относительно хоста. Локально совпадает с корнем.
    """
    env = os.getenv("SEAMLYAI_HOST_RENDER_ROOT")
    return Path(env).resolve() if env else default_render_root()


def default_async_out_dir() -> Path:
    """Каталог результатов async-job-ов."""
    env = os.getenv("SEAMLYAI_ASYNC_OUT_DIR")
    return Path(env).resolve() if env else default_render_root() / "async_out"


def _mount_view(path: Path) -> Path:
    """Возвращает путь, под которым `path` виден демону Docker на хосте."""
    root = default_render_root().resolve()
    host = host_mount_root().resolve()
    try:
        rel = path.resolve().relative_to(root)
    except ValueError:
        return path
    if host == root:
        return path
    return host / rel


# Поддерживаемые форматы вывода Seamly2D (для render_one.sh).
FORMATS: dict[str, dict[str, str]] = {
    "png": {"num": "3", "ext": "png", "media": "image/png"},
    "svg": {"num": "0", "ext": "svg", "media": "image/svg+xml"},
    "pdf": {"num": "1", "ext": "pdf", "media": "application/pdf"},
    "pdf-tiled": {"num": "2", "ext": "pdf", "media": "application/pdf"},
    "jpg": {"num": "4", "ext": "jpg", "media": "image/jpeg"},
    "dxf": {"num": "17", "ext": "dxf", "media": "application/dxf"},
    "dxf-aama": {"num": "19", "ext": "dxf", "media": "application/dxf"},
}


class RenderError(RuntimeError):
    """Ошибка рендера (непустой RC / нет файла результата)."""


class RenderUnavailable(RenderError):
    """Docker/образ недоступны — рендер невозможен."""


@dataclass
class RenderResult:
    file_path: Path
    log: str
    format: str = "png"


def _docker_available() -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run(
            [docker, "--version"], check=True, capture_output=True, timeout=10
        )
        return True
    except (subprocess.SubprocessError, OSError):
        return False


def render_pattern(
    template_key: str,
    measurements: dict[str, float],
    size: str | None = None,
    adjustments: dict[str, float] | None = None,
    out_dir: Path | None = None,
    format: str = "png",
) -> RenderResult:
    """Конвертирует шаблон, генерирует мерки и рендерит лекало через контейнер.

    `format` — ключ из FORMATS (png/svg/pdf/pdf-tiled/jpg/dxf/dxf-aama).
    """
    if format not in FORMATS:
        raise RenderError(f"Неизвестный формат: {format}. Доступны: {', '.join(FORMATS)}")
    tmpl = get_template(template_key)
    if not _docker_available():
        raise RenderUnavailable("Docker недоступен — установите Docker Desktop")

    fmt = FORMATS[format]
    tag = f"{template_key}_{(size or 'custom').replace(' ', '')}"
    job_dir = Path(tempfile.mkdtemp(prefix=f"seamly_{tag}_", dir=default_render_root()))
    out_base = out_dir or (job_dir.parent / f"{tag}_out")
    out_base.mkdir(parents=True, exist_ok=True)
    try:
        val_path = job_dir / f"{tag}.val"
        vit_path = job_dir / f"{tag}.vit"
        # 0.6.8-совместимый .val + путь к меркам рядом
        val_raw = tmpl.path.read_text(encoding="utf-8")
        val = _with_measurements_path(convert(val_raw), vit_path.name)
        if adjustments:
            from .generator import _apply_adjustments

            val = _apply_adjustments(val, adjustments)
        val_path.write_text(val, encoding="utf-8")
        vit_path.write_text(build_vit(measurements, template_key, size=size), encoding="utf-8")

        # bind-пути для демона Docker видятся со стороны хоста
        mount_job = _mount_view(job_dir)
        mount_out = _mount_view(out_base)
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{mount_job}:/job",
            "-v", f"{mount_out}:/out",
            RENDERER_IMAGE,
            "bash", "/usr/local/bin/render_one.sh",
            f"/job/{val_path.name}",
            f"/job/{vit_path.name}",
            tag,
            format,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log = (proc.stdout + "\n" + proc.stderr).strip()
        files = list(out_base.rglob(f"*.{fmt['ext']}"))
        if not files:
            detail = "You can't export empty scene" if "empty scene" in log else log
            raise RenderError(f"Рендер не дал файл (rc={proc.returncode}): {detail}")
        return RenderResult(file_path=files[0], log=log, format=format)
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)


def _with_measurements_path(val_xml: str, filename: str) -> str:
    import re

    return re.sub(
        r"<measurements>.*?</measurements>",
        f"<measurements>{filename}</measurements>",
        val_xml,
        flags=re.DOTALL,
    )