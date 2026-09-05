"""Headless-рендер лекала в PNG через Docker-контейнер Seamly2D.

Образ: `seamly-renderer:latest` (см. `ai-service/seamly-renderer/`).
Конвейер:
  1. сгенерировать .val (modern 0.6.8) и .vit рядом во временной job-папке;
  2. `docker run --rm` смонтировать job-папку и положить PNG в out-папку;
  3. вернуть путь к PNG (или структурированную ошибку).

Если Docker недоступен (нет бинаря/демона) — поднимается RenderUnavailable.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .converter import convert
from .generator import build_vit
from .templates import get_template

RENDERER_IMAGE = "seamly-renderer:latest"
_CONVERT_HOST_ROOT = Path(__file__).resolve().parent.parent.parent.parent / "seamly-renderer"


class RenderError(RuntimeError):
    """Ошибка рендера (непустой RC / нет PNG)."""


class RenderUnavailable(RenderError):
    """Docker/образ недоступны — рендер невозможен."""


@dataclass
class RenderResult:
    png_path: Path
    log: str


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
) -> RenderResult:
    """Конвертирует шаблон, генерирует мерки и рендерит PNG через контейнер."""
    tmpl = get_template(template_key)
    if not _docker_available():
        raise RenderUnavailable("Docker недоступен — установите Docker Desktop")

    tag = f"{template_key}_{(size or 'custom').replace(' ', '')}"
    job_dir = Path(tempfile.mkdtemp(prefix=f"seamly_{tag}_", dir=_CONVERT_HOST_ROOT))
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

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{job_dir}:/job",
            "-v", f"{out_base}:/out",
            RENDERER_IMAGE,
            "bash", "/usr/local/bin/render_one.sh",
            f"/job/{val_path.name}",
            f"/job/{vit_path.name}",
            tag,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        log = (proc.stdout + "\n" + proc.stderr).strip()
        pngs = list(out_base.rglob("*.png"))
        if not pngs:
            detail = "You can't export empty scene" if "empty scene" in log else log
            raise RenderError(f"Рендер не дал PNG (rc={proc.returncode}): {detail}")
        return RenderResult(png_path=pngs[0], log=log)
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