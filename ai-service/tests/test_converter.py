"""Тесты конвертера гибридной схемы .val -> 0.6.8 <draftBlock>+<pieces>."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pattern.converter import TARGET_VERSION, convert
from app.pattern.generator import build_vit
from app.pattern.measurement_names import SMLY_KNOWN_MEASUREMENTS

# Минимальный гибридный .val (по мотивам skirt.val)
_HYBRID = """<?xml version="1.0" encoding="UTF-8"?>
<pattern>
    <version>0.6.2</version>
    <unit>cm</unit>
    <description/>
    <notes/>
    <measurements>any/path/measures.vit</measurements>
    <increments>
        <increment description="" formula="45" name="#skirt_length"/>
    </increments>
    <draw name="Pattern piece 1">
        <calculation>
            <point firstPoint="2" id="4" mx="0.1" my="0.2" name="A4" secondPoint="3" showPointName="true" type="pointOfIntersection"/>
        </calculation>
        <modeling>
            <point id="62" idObject="1" inUse="true" mx="0" my="0" showPointName="true" type="modeling"/>
        </modeling>
        <details>
            <detail forbidFlipping="false" hideMainPath="false" id="82" inLayout="true" mx="5.6" my="0" name="Detail" seamAllowance="true" united="false" version="2" width="1">
                <nodes>
                    <node idObject="62" type="NodePoint"/>
                </nodes>
            </detail>
        </details>
        <groups/>
    </draw>
</pattern>
"""


def _count(html: str, needle: str) -> int:
    return len(re.findall(re.escape(needle), html))


def test_version_bumped():
    out = convert(_HYBRID)
    assert f"<version>{TARGET_VERSION}</version>" in out
    assert "0.6.2" not in out.split("<draw")[0]


def test_draw_becomes_draftblock():
    out = convert(_HYBRID)
    assert '<draftBlock name="Pattern piece 1">' in out
    assert "</draftBlock>" in out
    assert "<draw" not in out
    assert "</draw>" not in out


def test_patternLabel_inserted():
    out = convert(_HYBRID)
    assert "<patternLabel>" in out
    assert '<line alignment="0" ' in out


def test_detail_becomes_piece():
    out = convert(_HYBRID)
    assert "<pieces>" in out and "</pieces>" in out
    assert '<piece closed="1"' in out
    assert "</piece>" in out
    assert "<details>" not in out
    assert "<detail" not in out


def test_showPointName_removed():
    out = convert(_HYBRID)
    assert "showPointName" not in out


def test_point_of_intersection_converted():
    out = convert(_HYBRID)
    assert "pointOfIntersection" not in out
    m = re.search(
        r'<point[^>]*type="intersectXY"[^>]*>', out
    )
    assert m, "точка intersectXY не найдена"
    tag = m.group(0)
    assert 'lineColor="black"' in tag
    assert 'lineType="dashLine"' in tag
    assert 'lineWeight="0.35"' in tag


def test_seam_allowance_boolean_to_int():
    out = convert(_HYBRID)
    assert 'seamAllowance="1"' in out
    assert 'seamAllowance="true"' not in out


def test_convert_real_skirt_template():
    """Конвертация реального шаблона юбки: результат не содержит legacy."""
    content = (
        Path(__file__).resolve().parent.parent
        / "templates"
        / "skirt.val"
    ).read_text(encoding="utf-8")
    out = convert(content)
    assert "pointOfIntersection" not in out
    assert "<draftBlock" in out
    assert "<pieces>" in out


def test_build_vit_only_known_names():
    """Файл мерок не должен содержать нестандартные имена (валидность vit)."""
    xml = build_vit(
        {"waist_circ": 70, "hip_circ": 96, "waist_to_hip_b": 21},
        "skirt",
    )
    names = re.findall(r'<m name="([^"]+)"', xml)
    assert names, "в vit не найдено ни одной мерки"
    for name in names:
        assert name in SMLY_KNOWN_MEASUREMENTS, f"нестандартная мерка в vit: {name}"


def test_self_closing_details_converted():
    """Шаблоны без деталей (<details/>) тоже должны получить <pieces/>."""
    hybrid = _HYBRID.replace(
        "<details>\n"
        '            <detail forbidFlipping="false" hideMainPath="false" id="82"'
        ' inLayout="true" mx="5.6" my="0" name="Detail" seamAllowance="true"'
        ' united="false" version="2" width="1">\n'
        "                <nodes>\n"
        '                    <node idObject="62" type="NodePoint"/>\n'
        "                </nodes>\n"
        "            </detail>\n"
        "        </details>",
        "<details/>",
    )
    out = convert(hybrid)
    assert "<pieces/>" in out
    assert "<details/>" not in out


def test_point_of_intersection_arcs_kept():
    """pointOfIntersectionArcs — валидный тип в 0.6.8, его трогать нельзя."""
    hybrid = _HYBRID.replace(
        'type="pointOfIntersection"',
        'type="pointOfIntersectionArcs"',
    )
    out = convert(hybrid)
    assert 'type="pointOfIntersectionArcs"' in out


def test_convert_all_pool_templates():
    """Все шаблоны из реестра конвертируются в 0.6.8 без legacy-типов.

    Legacy-файлы (старее 0.6) пропускаются как есть: их конвертацией в 0.6.8
    занимается сам Seamly2D при открытии (наш convert такие не трогает).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.pattern.templates import TEMPLATES

    for tmpl in TEMPLATES.values():
        content = tmpl.path.read_text(encoding="utf-8")
        out = convert(content)
        m = re.search(r"<version>\s*([0-9]+\.[0-9]+\.[0-9]+)", out)
        version = tuple(int(x) for x in m.group(1).split(".")) if m else (0, 0, 0)
        if version < (0, 6, 0):
            assert out == content, f"{tmpl.key}: legacy-файл не должен меняться"
            assert "<measurements" in out, f"{tmpl.key}: повреждён legacy-файл"
            continue
        assert "<draftBlock" in out, f"{tmpl.key}: нет draftBlock"
        assert "<version>0.6.8</version>" in out, f"{tmpl.key}: не 0.6.8"
        assert not re.search(
            r'type="pointOfIntersection"', out
        ), f"{tmpl.key}: остался legacy pointOfIntersection"


if __name__ == "__main__":
    test_version_bumped()
    test_draw_becomes_draftblock()
    test_patternLabel_inserted()
    test_detail_becomes_piece()
    test_showPointName_removed()
    test_point_of_intersection_converted()
    test_seam_allowance_boolean_to_int()
    test_convert_real_skirt_template()
    test_build_vit_only_known_names()
    test_self_closing_details_converted()
    test_point_of_intersection_arcs_kept()
    test_convert_all_pool_templates()
    print("ALL CONVERTER TESTS PASSED")