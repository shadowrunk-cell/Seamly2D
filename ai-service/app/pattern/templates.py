"""Реестр шаблонов паттернов Seamly (VIT).

Определяет доступные шаблоны, какие мерки им нужны, и как получить
требуемые мерки, если пользователь их не указал.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


@dataclass
class TemplateInfo:
    """Информация о шаблоне паттерна."""

    key: str
    filename: str
    display_name: str
    description: str
    # Имена мерок, которые реально используются в формулах шаблона
    required_measurements: list[str] = field(default_factory=list)
    # Основные "базовые" мерки, из которых можно вывести остальные
    base_measurements: list[str] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return TEMPLATES_DIR / self.filename


TEMPLATES: dict[str, TemplateInfo] = {
    "bodice": TemplateInfo(
        key="bodice",
        filename="bodice.val",
        display_name="Базовый лиф",
        description="Базовый лиф (bodice block) по Darragh Starr. "
        "Параметрический, с вытачками и плечевым швом.",
        required_measurements=[
            "bust_circ", "waist_circ", "bustpoint_to_bustpoint",
            "across_chest_f", "bustpoint_to_waist_front", "neck_front_to_bust_f",
            "bustpoint_to_shoulder_center", "bustpoint_to_shoulder_tip",
            "neck_width", "armscye_length", "armpit_to_waist_side",
            "waist_arc_b", "bust_arc_b", "across_back_b", "bust_to_waist_b",
            "neck_back_to_waist_b", "across_back_to_waist_b", "shoulder_length",
            "hip_circ", "hip_arc_b", "highhip_circ", "highhip_arc_b",
        ],
        base_measurements=["bust_circ", "waist_circ", "hip_circ"],
    ),
    "skirt": TemplateInfo(
        key="skirt",
        filename="skirt.val",
        display_name="Базовая юбка",
        description="Базовый слопер юбки по TheShapesOfFabric. "
        "Параметрическая длина (#skirt_length) и прибавки (#waist_ease, #hip_ease).",
        required_measurements=["waist_circ", "hip_circ", "waist_to_hip_b"],
        base_measurements=["waist_circ", "hip_circ"],
    ),
    "trousers": TemplateInfo(
        key="trousers",
        filename="trousers.val",
        display_name="Базовые брюки",
        description="Базовый слопер брюк по TheShapesOfFabric. "
        "Параметрические высоты и прибавки.",
        required_measurements=[
            "height_waist_front", "height_hip", "height_knee", "height_ankle",
            "leg_crotch_to_floor", "waist_circ", "hip_circ",
        ],
        base_measurements=["waist_circ", "hip_circ", "height_waist_front"],
    ),
}


def get_template(key: str) -> TemplateInfo:
    if key not in TEMPLATES:
        raise KeyError(
            f"Шаблон '{key}' не найден. Доступные: {list(TEMPLATES.keys())}"
        )
    return TEMPLATES[key]
