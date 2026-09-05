"""Построение пула изделий для рендера.

Для каждого шаблона из реестра:
  1. конвертирует гибридный .val -> современную схему 0.6.8 (draftBlock+pieces);
  2. генерирует .vit мерок под несколько стандартных размеров;
  3. прописывает в .val путь к соответствующему .vit.

Итог — набор пар (pattern.val, measures.vit), готовый к прогону
`seamly2d <abs val> -m <abs vit> -b <name> -d <out> -f 3 --exportOnlyDetails`.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pattern.converter import convert  # noqa: E402
from app.pattern.generator import build_vit  # noqa: E402
from app.pattern.templates import TEMPLATES  # noqa: E402

# Размеры SeamlyMe (ключи STANDARD_SIZES) для пула по категориям.
SIZES_BY_CATEGORY: dict[str, list[str]] = {
    "лифы": ["Size 8", "Size 12"],
    "корсеты": ["Size 8", "Size 12"],
    "юбки": ["Size 10", "Size 14"],
    "брюки": ["Size 12", "Size 16"],
}

# Базовые мерки, которые размеры не покрывают (вертикальные для брюк и т.п.).
EXTRA_BASE: dict[str, dict[str, float]] = {
    "trousers": {"height_waist_front": 106, "height": 165},
}


def build_pool(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    produced: list[Path] = []
    for key, tmpl in TEMPLATES.items():
        src = tmpl.path
        val = convert(src.read_text(encoding="utf-8"))
        for size in SIZES_BY_CATEGORY.get(tmpl.category, ["Size 12"]):
            item = f"{key}_{size.replace(' ', '')}"
            val_path = out_dir / f"{item}.val"
            vit_path = out_dir / f"{item}.vit"
            # путь к меркам — относительное имя рядом с объектом
            # (реальный абсолютный задаётся через -m на рендере)
            val_with_meas = _set_measurements_path(val, vit_path.name)
            val_path.write_text(val_with_meas, encoding="utf-8")
            extra = EXTRA_BASE.get(key, {})
            vit_path.write_text(build_vit(extra, key, size=size), encoding="utf-8")
            produced.append(vit_path)
        print(f"[ok] {key}: конвертирован, sizes={SIZES_BY_CATEGORY.get(tmpl.category, ['Size 12'])}")
    return produced


def _set_measurements_path(val_xml: str, filename: str) -> str:
    import re

    return re.sub(
        r"<measurements>.*?</measurements>",
        f"<measurements>{filename}</measurements>",
        val_xml,
        flags=re.DOTALL,
    )


if __name__ == "__main__":
    default_out = Path(__file__).resolve().parent.parent.parent / "seamly-renderer" / "pool"
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else default_out
    items = build_pool(out)
    print(f"\nИтого изделий в пуле: {len(items)} -> {out}")