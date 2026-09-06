"""Реестр шаблонов паттернов (VIT).

Определяет доступные шаблоны-изделия, какие мерки им нужны, и как
получить требуемые мерки, если пользователь их не указал.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

# Возможные виды изделий (для фильтра каталога)
GARMENT_CATEGORIES: list[str] = [
    "лифы",
    "юбки",
    "брюки",
    "корсеты",
]
# Пол: female / male / unisex (отображаем в UI по-русски)
GENDERS: list[str] = ["female", "male", "unisex"]


@dataclass
class TemplateInfo:
    """Информация о шаблоне-изделии."""

    key: str
    filename: str
    display_name: str
    description: str
    # Вид изделия (категория) для фильтра: "лифы", "юбки", ...
    category: str = "лифы"
    # Пол: "female" | "male" | "unisex"
    gender: str = "female"
    # Путь к картинке-превью (URL, отдаётся статикой) или None
    image: str | None = None
    # Имена мерок, которые реально используются в формулах шаблона
    required_measurements: list[str] = field(default_factory=list)
    # Основные "базовые" мерки, из которых можно вывести остальные
    base_measurements: list[str] = field(default_factory=list)

    @property
    def path(self) -> Path:
        return TEMPLATES_DIR / self.filename


# Реально используемые мерки корсетов/лифов Mandy Barrington (без hip_circ —
# он есть только в corset_1875/corset_1890/bodice_mb).
_CORSET_MEASUREMENTS_BASE = [
    "bust_circ", "waist_circ",
    "bustpoint_to_bustpoint", "across_back_b", "across_chest_f",
    "neck_back_to_waist_b", "neck_circ", "waist_to_hip_b",
]
# Корсеты с привязкой длины к росту (Mandy Barrington использует #height).
_CORSET_MEASUREMENTS_HEIGHT = _CORSET_MEASUREMENTS_BASE + ["height"]
# Корсеты, в которых задействован обхват бёдер.
_CORSET_MEASUREMENTS_HIP = _CORSET_MEASUREMENTS_HEIGHT + ["hip_circ"]
# Лиф Mandy Barrington: рост не используется, но hip_circ нужен.
_BODICE_MB_MEASUREMENTS = _CORSET_MEASUREMENTS_BASE + ["hip_circ"]

TEMPLATES: dict[str, TemplateInfo] = {
    "bodice": TemplateInfo(
        key="bodice",
        filename="bodice.val",
        display_name="Базовый лиф",
        description="Базовый лиф (bodice block) по Darragh Starr. "
        "Параметрический, с вытачками и плечевым швом.",
        category="лифы",
        gender="female",
        image=None,
        required_measurements=[
            "bust_circ", "waist_circ", "bustpoint_to_bustpoint",
            "across_chest_f", "bustpoint_to_waist_front", "neck_front_to_bust_f",
            "bustpoint_to_shoulder_center", "bustpoint_to_shoulder_tip",
            "neck_width", "armscye_length", "armpit_to_waist_side",
            "waist_arc_b", "bust_arc_b",
            "across_back_b", "bust_to_waist_b",
            "neck_back_to_waist_b", "across_back_to_waist_b", "shoulder_length",
            "hip_circ", "hip_arc_b", "highhip_circ",
            "highhip_arc_b", "height",
        ],
        base_measurements=["bust_circ", "waist_circ", "hip_circ"],
    ),
    "bodice_mb": TemplateInfo(
        key="bodice_mb",
        filename="bodice_mb.val",
        display_name="Лиф (Mandy Barrington)",
        description="Женский лиф по методике Mandy Barrington. "
        "Основная выкройка-основа полочки и спинки.",
        category="лифы",
        gender="female",
        image="/img/bodice_mb.png",
        required_measurements=_BODICE_MB_MEASUREMENTS,
        base_measurements=["bust_circ", "waist_circ"],
    ),
    "skirt": TemplateInfo(
        key="skirt",
        filename="skirt.val",
        display_name="Базовая юбка",
        description="Базовый слопер юбки по TheShapesOfFabric. "
        "Параметрическая длина (#skirt_length) и прибавки (#waist_ease, #hip_ease).",
        category="юбки",
        gender="female",
        image="/img/skirt.png",
        required_measurements=["waist_circ", "hip_circ", "waist_to_hip_b", "height"],
        base_measurements=["waist_circ", "hip_circ"],
    ),
    "trousers": TemplateInfo(
        key="trousers",
        filename="trousers.val",
        display_name="Базовые брюки",
        description="Базовый слопер брюк по TheShapesOfFabric. "
        "Параметрические высоты и прибавки.",
        category="брюки",
        gender="unisex",
        image="/img/trousers.png",
        required_measurements=[
            "height_waist_front", "height_hip", "height_knee", "height_ankle",
            "leg_crotch_to_floor", "waist_circ", "hip_circ", "height",
        ],
        base_measurements=["waist_circ", "hip_circ", "height_waist_front"],
    ),
    "corset_base": TemplateInfo(
        key="corset_base",
        filename="corset_base.val",
        display_name="Корсет-основа",
        description="Базовая выкройка корсета по Mandy Barrington без "
        "косточек и декора — основа для моделирования.",
        category="корсеты",
        gender="female",
        image="/img/corset_base.png",
        required_measurements=[
            "bust_circ", "bustpoint_to_bustpoint",
            "across_back_b", "across_chest_f",
            "neck_back_to_waist_b", "neck_circ", "waist_to_hip_b",
        ],
        base_measurements=["bust_circ"],
    ),
    "corset_1598": TemplateInfo(
        key="corset_1598",
        filename="corset_1598.val",
        display_name="Корсет «Пара шарнирных»",
        description="Исторический корсет 1598 года (pair of bodies) "
        "по Mandy Barrington.",
        category="корсеты",
        gender="female",
        image="/img/corset_1598.png",
        required_measurements=_CORSET_MEASUREMENTS_HEIGHT,
        base_measurements=["bust_circ", "waist_circ"],
    ),
    "corset_1735": TemplateInfo(
        key="corset_1735",
        filename="corset_1735.val",
        display_name="Корсет 1735 (полностью косточковый)",
        description="Полностью косточковый корсет 1735 года по "
        "Mandy Barrington.",
        category="корсеты",
        gender="female",
        image="/img/corset_1735.png",
        required_measurements=_CORSET_MEASUREMENTS_HEIGHT,
        base_measurements=["bust_circ", "waist_circ"],
    ),
    "corset_1875": TemplateInfo(
        key="corset_1875",
        filename="corset_1875.val",
        display_name="Корсет 1875 (шнурованный и стёганый)",
        description="Шнурованный и стёганый корсет 1875 года по "
        "Mandy Barrington.",
        category="корсеты",
        gender="female",
        image="/img/corset_1875.png",
        required_measurements=_CORSET_MEASUREMENTS_HIP,
        base_measurements=["bust_circ", "waist_circ"],
    ),
    "corset_1890": TemplateInfo(
        key="corset_1890",
        filename="corset_1890.val",
        display_name="Свадебный корсет 1890",
        description="Свадебный корсет Celebrated C.B. Bridal 1890 года "
        "по Mandy Barrington.",
        category="корсеты",
        gender="female",
        image="/img/corset_1890.png",
        required_measurements=_CORSET_MEASUREMENTS_HIP,
        base_measurements=["bust_circ", "waist_circ"],
    ),
}


def get_template(key: str) -> TemplateInfo:
    if key not in TEMPLATES:
        raise KeyError(
            f"Шаблон '{key}' не найден. Доступные: {list(TEMPLATES.keys())}"
        )
    return TEMPLATES[key]
