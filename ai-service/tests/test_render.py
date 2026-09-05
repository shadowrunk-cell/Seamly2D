"""Тесты рендера лекал в PNG (через Docker-контейнер)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pattern.render import (  # noqa: E402
    RenderError,
    RenderUnavailable,
    _with_measurements_path,
    render_pattern,
)


def test_measurements_path_injected():
    val = "<measurements>old/path.vit</measurements>"
    out = _with_measurements_path(val, "measures.vit")
    assert "<measurements>measures.vit</measurements>" in out


def test_render_pattern_empty_measurements_fails_without_docker(monkeypatch):
    """Без Docker эндпоинт даёт RenderUnavailable, а не исключение из-за файлов."""
    monkeypatch.setattr("app.pattern.render._docker_available", lambda: False)
    with pytest.raises(RenderUnavailable):
        render_pattern(
            template_key="skirt",
            measurements={"waist_circ": 70, "hip_circ": 96},
            size="Size 10",
        )


def test_render_pattern_with_mocked_docker(monkeypatch, tmp_path):
    class _Proc:
        returncode = 0
        stdout = "OK"
        stderr = ""

    def _fake_run(cmd, capture_output=False, text=False, timeout=0):
        # cmd содержит: ... -v <host>:/job ... -v <host>:/out ... IMAGE val vit base
        host_out = None
        for item in cmd:
            if item.endswith(":/out"):
                host_out = Path(item[: -len(":/out")])
        assert host_out, f"нет монтирования ':/out' в cmd={cmd}"
        host_out.mkdir(parents=True, exist_ok=True)
        (host_out / "piece.png").write_bytes(b"PNGDATA")
        return _Proc()

    monkeypatch.setattr("app.pattern.render._docker_available", lambda: True)
    monkeypatch.setattr("app.pattern.render.subprocess.run", _fake_run)
    result = render_pattern(
        template_key="skirt",
        measurements={"waist_circ": 70, "hip_circ": 96},
        size="Size 10",
        out_dir=tmp_path,
    )
    assert result.png_path.exists()
    assert result.png_path.read_bytes() == b"PNGDATA"