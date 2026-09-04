"""Тесты генерации мерок (без LLM)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.pattern import measurements
from app.pattern.generator import build_full_measurement_table, build_vit, generate_pattern
from app.pattern.models import MeasurementInput, PatternRequest


def test_build_table_basic():
    table, missing = build_full_measurement_table(
        {"waist_circ": 70, "hip_circ": 96}, template_key="skirt"
    )
    assert table["waist_circ"] == 70
    assert table["hip_circ"] == 96
    assert "waist_to_hip_b" in table  # вычисляется дефолтом


def test_size_fills_bods():
    table, _ = build_full_measurement_table(
        {}, size="Size 10", template_key="bodice"
    )
    assert table["bust_circ"] == 86
    assert table["waist_circ"] == 68
    assert table["hip_circ"] == 92


def test_derived_measurements():
    table, _ = build_full_measurement_table(
        {"bust_circ": 90, "waist_circ": 70, "hip_circ": 94}, template_key="bodice"
    )
    # базовые производные мерки должны быть добавлены
    assert "bust_arc_b" in table
    assert "across_chest_f" in table
    assert "neck_width" in table
    assert "shoulder_length" in table


def test_vit_xml_generation():
    xml = build_vit({"waist_circ": 70}, "skirt")
    assert "<m name=\"waist_circ\" value=\"70\"" in xml
    assert "<unit>cm</unit>" in xml


def test_generate_pattern_val():
    req = PatternRequest(
        template="skirt",
        measurements=[
            MeasurementInput(name="waist_circ", value=70),
            MeasurementInput(name="hip_circ", value=96),
            MeasurementInput(name="waist_to_hip_b", value=21),
        ],
        adjustments={"#skirt_length": 60},
    )
    result = generate_pattern(req)
    assert result.filename.endswith(".val")
    assert "<pattern>" in result.content
    assert "<measurements>measurements_skirt.vit</measurements>" in result.content
    # инкремент длины юбки должен измениться
    assert 'name="#skirt_length"' in result.content.replace("#", "#")
    assert 'formula="45"' not in result.content.replace('name="#skirt_length"', "")
    assert result.applied_measurements["waist_circ"] == 70


def test_generate_pattern_adjustment():
    req = PatternRequest(
        template="skirt",
        measurements=[MeasurementInput(name="waist_circ", value=70)],
        adjustments={"#skirt_length": 70},
    )
    result = generate_pattern(req)
    # #skirt_length formula должен стать 70
    import re
    m = re.search(r'<increment[^>]*name="#skirt_length"[^>]*formula="([^"]+)"[^>]*>', result.content)
    if not m:
        m = re.search(r'<increment[^>]*formula="([^"]+)"[^>]*name="#skirt_length"[^>]*>', result.content)
    assert m, "инкремент #skirt_length не найден"
    assert m.group(1) == "70"


if __name__ == "__main__":
    test_build_table_basic()
    test_size_fills_bods()
    test_derived_measurements()
    test_vit_xml_generation()
    test_generate_pattern_val()
    test_generate_pattern_adjustment()
    print("ALL TESTS PASSED")
