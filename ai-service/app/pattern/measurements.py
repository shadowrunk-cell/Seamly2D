"""Генерация файла мерок (.vit) для паттерна.

SeamlyMe использует файл мерок определенного формата:
  <vit><body-measurements><m name="..." value="..."/></body-measurements></vit>
Формулы в .val обращаются к этим именам мерок.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from .models import MeasurementInput

# Стандартные размеры SeamlyMe (взяты из Mandy Barrington/Sizes).
# Используются, когда пользователь не предоставил мерку, указав размер.
STANDARD_SIZES: dict[str, dict[str, float]] = {
    "Size 6": {
        "bust_circ": 80, "lowbust_circ": 68, "waist_circ": 62, "hip_circ": 86,
        "across_back_b": 32, "neck_back_to_waist_b": 38.5, "across_chest_f": 29,
        "bustpoint_to_bustpoint": 17.5, "waist_to_hip_b": 20, "neck_circ": 34,
    },
    "Size 8": {
        "bust_circ": 82, "lowbust_circ": 70, "waist_circ": 64, "hip_circ": 88,
        "across_back_b": 32.5, "neck_back_to_waist_b": 39, "across_chest_f": 29.5,
        "bustpoint_to_bustpoint": 18, "waist_to_hip_b": 20, "neck_circ": 34.5,
    },
    "Size 10": {
        "bust_circ": 86, "lowbust_circ": 74, "waist_circ": 68, "hip_circ": 92,
        "across_back_b": 34, "neck_back_to_waist_b": 39.5, "across_chest_f": 31,
        "bustpoint_to_bustpoint": 19, "waist_to_hip_b": 20.5, "neck_circ": 36,
    },
    "Size 12": {
        "bust_circ": 90, "lowbust_circ": 78, "waist_circ": 72, "hip_circ": 96,
        "across_back_b": 35, "neck_back_to_waist_b": 40.5, "across_chest_f": 32,
        "bustpoint_to_bustpoint": 20, "waist_to_hip_b": 21.5, "neck_circ": 37,
    },
    "Size 14": {
        "bust_circ": 94, "lowbust_circ": 82, "waist_circ": 76, "hip_circ": 100,
        "across_back_b": 36, "neck_back_to_waist_b": 41.5, "across_chest_f": 33,
        "bustpoint_to_bustpoint": 21, "waist_to_hip_b": 22.5, "neck_circ": 38,
    },
    "Size 16": {
        "bust_circ": 98, "lowbust_circ": 86, "waist_circ": 80, "hip_circ": 104,
        "across_back_b": 37, "neck_back_to_waist_b": 42, "across_chest_f": 34,
        "bustpoint_to_bustpoint": 22, "waist_to_hip_b": 23, "neck_circ": 39,
    },
    "Size 18": {
        "bust_circ": 102, "lowbust_circ": 90, "waist_circ": 84, "hip_circ": 108,
        "across_back_b": 38, "neck_back_to_waist_b": 43, "across_chest_f": 35,
        "bustpoint_to_bustpoint": 23, "waist_to_hip_b": 23.5, "neck_circ": 40,
    },
    "Size 20": {
        "bust_circ": 106, "lowbust_circ": 94, "waist_circ": 88, "hip_circ": 112,
        "across_back_b": 39, "neck_back_to_waist_b": 44, "across_chest_f": 36,
        "bustpoint_to_bustpoint": 24, "waist_to_hip_b": 24, "neck_circ": 41,
    },
    "Size 22": {
        "bust_circ": 110, "lowbust_circ": 98, "waist_circ": 92, "hip_circ": 116,
        "across_back_b": 40, "neck_back_to_waist_b": 45, "across_chest_f": 37,
        "bustpoint_to_bustpoint": 25, "waist_to_hip_b": 24.5, "neck_circ": 42,
    },
    "Size 24": {
        "bust_circ": 114, "lowbust_circ": 102, "waist_circ": 96, "hip_circ": 120,
        "across_back_b": 41, "neck_back_to_waist_b": 46, "across_chest_f": 38,
        "bustpoint_to_bustpoint": 26, "waist_to_hip_b": 25, "neck_circ": 43,
    },
}

# Разумные значения по умолчанию, когда ни пользователь, ни размер
# не дали мерку (чтобы файл всегда был валидным).
DEFAULT_MEASUREMENTS: dict[str, float] = {
    "bust_circ": 90, "waist_circ": 70, "hip_circ": 94,
    "waist_to_hip_b": 21, "neck_back_to_waist_b": 40,
    "across_back_b": 35, "across_chest_f": 32, "neck_circ": 36,
    "bustpoint_to_bustpoint": 19.5, "height": 165,
}


def _format_value(value: float) -> str:
    """Форматирует число компактно."""
    if value == int(value):
        return str(int(value))
    return f"{value:g}"


def build_measurement_table(
    user_measurements: list[MeasurementInput],
    size: Optional[str] = None,
) -> dict[str, float]:
    """Собирает итоговую таблицу мерок в см.

    Приоритет: пользовательские мерки > стандартный размер > дефолт.
    Возвращает: имя мерки -> значение (float).
    """
    table: dict[str, float] = {}
    for m in user_measurements:
        table[m.name] = m.value

    if size and size in STANDARD_SIZES:
        for name, val in STANDARD_SIZES[size].items():
            table.setdefault(name, val)

    for name, val in DEFAULT_MEASUREMENTS.items():
        table.setdefault(name, val)

    return table


def build_vit_measurements(
    user_measurements: list[MeasurementInput],
    size: Optional[str] = None,
) -> str:
    """Генерирует содержимое файла мерок .vit."""
    table = build_measurement_table(user_measurements, size)

    vit = ET.Element("vit")
    ver = ET.SubElement(vit, "version")
    ver.text = "0.3.3"
    ro = ET.SubElement(vit, "read-only")
    ro.text = "false"
    notes = ET.SubElement(vit, "notes")
    unit = ET.SubElement(vit, "unit")
    unit.text = "cm"
    pm = ET.SubElement(vit, "pm_system")
    pm.text = "998"
    personal = ET.SubElement(vit, "personal")
    ET.SubElement(personal, "family-name")
    ET.SubElement(personal, "given-name")
    bd = ET.SubElement(personal, "birth-date")
    bd.text = "1800-01-01"
    g = ET.SubElement(personal, "gender")
    g.text = "unknown"
    ET.SubElement(personal, "email")

    body = ET.SubElement(vit, "body-measurements")
    for name in sorted(table.keys()):
        m = ET.SubElement(body, "m")
        m.set("name", name)
        m.set("value", _format_value(table[name]))

    ET.indent(vit, space="    ")
    return ET.tostring(vit, encoding="unicode", xml_declaration=True)


def write_vit_measurements(
    path: Path,
    user_measurements: list[MeasurementInput],
    size: Optional[str] = None,
) -> dict[str, float]:
    """Записывает файл мерок .vit на диск. Возвращает таблицу мерок."""
    content = build_vit_measurements(user_measurements, size)
    path.write_text(content, encoding="utf-8")
    return build_measurement_table(user_measurements, size)
