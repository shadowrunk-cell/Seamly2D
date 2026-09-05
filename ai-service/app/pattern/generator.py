"""Генерация файла мерок (.vit) и паттерна (.val) для Seamly.

Конвейер:
  1. Пользователь даёт мерки (частично) + выбирает шаблон
  2. Недостающие мерки выводятся из базовых (bust/waist/hip/height)
     или из стандартного размера, или из разумных значений по умолчанию
  3. Генерируется файл мерок (.vit) рядом с паттерном
  4. В шаблоне (.val) заменяется путь к меркам и корректируются инкременты
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

from .models import PatternRequest, PatternResponse
from .templates import get_template
from .measurement_names import SMLY_KNOWN_MEASUREMENTS


def _val(v: float) -> str:
    """Компактное форматирование числа."""
    if v == int(v):
        return str(int(v))
    return f"{v:g}"


# ------------------------------------------------------------------
# Вывод недостающих мерок из базовых (пропорции типового женского тела)
# ------------------------------------------------------------------
def derive_measurements(basic: dict[str, float]) -> dict[str, float]:
    """Достраивает производные мерки из базовых (bust/waist/hip/height)."""
    d: dict[str, float] = {}
    bust = basic.get("bust_circ")
    waist = basic.get("waist_circ")
    hip = basic.get("hip_circ")
    height = basic.get("height_waist_front") or basic.get("height")

    if bust:
        d.setdefault("bust_point", bust / 2)  # полобхвата груди
    if hip:
        d.setdefault("hip_point", hip / 2)

    # Полу-обхваты (имена, встречающиеся в строении)
    if bust:
        d.setdefault("bust_arc_b", bust / 2)
        d.setdefault("lowbust_circ", bust - 12)
        d.setdefault("bustpoint_to_bustpoint", bust * 0.21)
        d.setdefault("bust_to_waist_b", (bust - waist) * 0.31 if waist else 17)
        d.setdefault("neck_front_to_bust_f", 25)
        d.setdefault("bustpoint_to_shoulder_center", 18)
        d.setdefault("bustpoint_to_shoulder_tip", 20)
        d.setdefault("bustpoint_to_waist_front", 20)
        d.setdefault("across_chest_f", bust * 0.36)
        d.setdefault("armscye_length", bust * 0.45)
        d.setdefault("armpit_to_waist_side", 15)
        d.setdefault("shoulder_length", 12.5)
        d.setdefault("neck_width", 12.5)

    if waist:
        d.setdefault("waist_arc_b", waist / 2)
        d.setdefault("waist_to_hip_b", 20.5)

    if hip:
        # Таз/бёдра: перед/спинка и высокие бёдра
        d.setdefault("highhip_circ", hip * 0.96)
        d.setdefault("hip_arc_b", hip / 2)
        d.setdefault("highhip_arc_b", d["highhip_circ"] / 2)
        d.setdefault("hip_arc_f", hip / 2)
        d.setdefault("highhip_arc_f", d["highhip_circ"] / 2)

    d.setdefault("across_back_b", 35)
    d.setdefault("neck_back_to_waist_b", 40)
    d.setdefault("across_back_to_waist_b", 22)
    d.setdefault("neck_circ", 36)

    # Брюки — вертикальные мерки, если дан рост
    if height:
        d.setdefault("height_hip", height - 20)
        d.setdefault("height_knee", height - 60)
        d.setdefault("height_ankle", height - 104)
        d.setdefault("leg_crotch_to_floor", height - 26)
    return d


# ------------------------------------------------------------------
# Сборка итоговой таблицы мерок
# ------------------------------------------------------------------
def build_full_measurement_table(
    user_measurements: dict[str, float],
    size: Optional[str] = None,
    template_key: Optional[str] = None,
) -> tuple[dict[str, float], list[str]]:
    """Собирает полную таблицу мерок и список недостающих.

    Приоритет: пользователь > размер > вывод из базовых > дефолты.
    Возвращает (таблица, недостающие_шаблону_мерки).
    """
    table = dict(user_measurements)

    # 1. Стандартный размер
    from .measurements import STANDARD_SIZES

    if size and size in STANDARD_SIZES:
        for name, val in STANDARD_SIZES[size].items():
            table.setdefault(name, val)

    # 2. Вывод из базовых
    derived = derive_measurements(table)
    for name, val in derived.items():
        table.setdefault(name, val)

    missing: list[str] = []
    if template_key:
        tmpl = get_template(template_key)
        for name in tmpl.required_measurements:
            if name not in table:
                missing.append(name)

    # 3. Любые оставшиеся недостающие шаблону — затыкаем дефолтами,
    #    чтобы файл всегда был валидным
    from .measurements import DEFAULT_MEASUREMENTS

    for name in missing:
        if name in DEFAULT_MEASUREMENTS:
            table[name] = DEFAULT_MEASUREMENTS[name]

    return table, missing


# ------------------------------------------------------------------
# Файл мерок .vit
# ------------------------------------------------------------------
def build_vit(
    user_measurements: dict[str, float],
    template_key: str,
    size: Optional[str] = None,
) -> str:
    """Собирает XML .vit-файла мерок, содержащий ВСЕ мерки шаблона."""
    table, _ = build_full_measurement_table(
        user_measurements, size=size, template_key=template_key
    )

    vit = ET.Element("vit")
    ET.SubElement(vit, "version").text = "0.3.3"
    ET.SubElement(vit, "read-only").text = "false"
    ET.SubElement(vit, "unit").text = "cm"
    ET.SubElement(vit, "pm_system").text = "998"
    personal = ET.SubElement(vit, "personal")
    for _child in ("family-name", "given-name"):
        ET.SubElement(personal, _child).text = ""
    ET.SubElement(personal, "birth-date").text = "1990-01-01"
    ET.SubElement(personal, "gender").text = "female"
    ET.SubElement(personal, "email").text = ""
    body = ET.SubElement(vit, "body-measurements")
    # .vit — файл пользовательских мерок: содержит ТОЛЬКО стандартные имена
    # Seamly. Нестандартные производные (bust_point, hip_point и т.п.) в файл
    # не попадают — иначе Seamly падает с "invalid known measurement(s)".
    for name in sorted(table.keys()):
        if name not in SMLY_KNOWN_MEASUREMENTS:
            continue
        ET.SubElement(body, "m", name=name, value=_val(table[name]))
    ET.indent(vit, space="    ")
    return ET.tostring(vit, encoding="unicode", xml_declaration=True)


# ------------------------------------------------------------------
# Инъекция пути к меркам и корректировка инкрементов в .val
# ------------------------------------------------------------------
def _apply_adjustments(val_xml: str, adjustments: dict[str, float]) -> str:
    """Обновляет значения инкрементов (name -> число) в .val.

    Выполняется точечной заменой строк внутри <increment ...>, чтобы не
    трогать остальную структуру XML (важно для совместимости с CAD).
    """
    if not adjustments:
        return val_xml

    import re

    for name, value in adjustments.items():
        # Ищем <increment ... name="<name>" ...>, у которого есть formula="..."
        # Меняем только значение formula у этого инкремента.
        def replace_formula(match: re.Match) -> str:
            tag = match.group(0)
            if name not in tag:
                return tag
            updated = re.sub(r'formula="[^"]*"', f'formula="{_val(value)}"', tag, count=1)
            return updated

        pattern = re.compile(r"<increment[^>]*name=\"" + re.escape(name) + r"\"[^>]*>")
        val_xml, n = pattern.subn(replace_formula, val_xml)
        if n == 0:
            # вдруг порядок атрибутов другой: name позже formula
            pattern2 = re.compile(r"<increment[^>]*formula=\"[^\"]*\"[^>]*name=\"" + re.escape(name) + r"\"[^>]*>")
            val_xml = pattern2.sub(replace_formula, val_xml)
    return val_xml


def generate_pattern(req: PatternRequest) -> PatternResponse:
    """Главная функция: генерирует паттерн из запроса."""
    tmpl = get_template(req.template)

    user_cm = req.to_cm

    # Собираем таблицу мерок и пишем файл мерок рядом с паттерном
    table, missing = build_full_measurement_table(
        user_cm, size=req.size, template_key=req.template
    )

    # Загружаем шаблон .val
    template_content = tmpl.path.read_text(encoding="utf-8")

    # Корректируем инкременты
    if req.adjustments:
        template_content = _apply_adjustments(template_content, req.adjustments)

    # Путь к файлу мерок. Seamly ожидает относительный/абсолютный путь.
    measurements_vit_file = "measurements_" + req.template + ".vit"
    # Подставляем вместо старого пути (может быть абсолютным). Меняем на соседний файл.
    # Заменяем всё между <measurements> и </measurements> на имя файла.
    template_content = _set_measurements_path(template_content, measurements_vit_file)

    return PatternResponse(
        filename=f"{req.template}_{'custom' if req.size is None else req.size}.val",
        content=template_content,
        template=req.template,
        applied_measurements=table,
        missing_measurements=sorted(set(missing) - set(table.keys())),
        warnings=_build_warnings(missing, req),
    )


def _set_measurements_path(val_xml: str, filename: str) -> str:
    import re

    return re.sub(r"<measurements>.*?</measurements>", f"<measurements>{filename}</measurements>", val_xml, flags=re.DOTALL)


def _build_warnings(missing: list[str], req: PatternRequest) -> list[str]:
    warnings: list[str] = []
    if missing:
        warnings.append(
            "Не все мерки предоставлены. Недостающие вычислены по "
            f"пропорциям: {', '.join(missing)}"
        )
    if req.size:
        warnings.append(f"Использован стандартный размер {req.size} для недостающих мерок.")
    return warnings
