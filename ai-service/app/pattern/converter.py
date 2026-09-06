"""Конвертация гибридных .val (старая схема <draw>+<details>)
в современную схему 0.6.8 (<draftBlock>+<pieces>).

Текущий бинарь Seamly2D (0.6.8) открывает только «модерн»-схему;
legacy-тип точки ``pointOfIntersection`` в schema 0.6.8 отсутствует и
мапится Seamly на ``intersectXY`` (VPatternConverter::toVersion0_6_4) с
добавлением line-атрибутов — здесь делается то же самое.

Внимание: преобразования строковые (regexp), а не через ElementTree:
XML-дерево меняло бы порядок атрибутов и распаковывало сущности формул,
ломая CAD-файл.
"""
from __future__ import annotations

import argparse
import re

TARGET_VERSION = "0.6.8"


def _convert_detail_opening(tag: str) -> str:
    """<detail ...> -> <piece closed="1" ...> с приведением атрибутов."""
    tag = re.sub(r'\s+inLayout="[^"]*"', "", tag)
    tag = re.sub(r'\s+united="[^"]*"', "", tag)
    tag = re.sub(r'\s+forbidFlipping="[^"]*"', "", tag)
    tag = re.sub(r'\s+hideMainPath="[^"]*"', "", tag)
    tag = re.sub(r'seamAllowance="true"', 'seamAllowance="1"', tag)
    tag = re.sub(r'seamAllowance="false"', 'seamAllowance="0"', tag)
    if re.search(r'\sclosed="[^"]*"', tag):
        tag = tag.replace("<detail", "<piece", 1)
    else:
        tag = tag.replace("<detail", '<piece closed="1"', 1)
    return tag


def convert(text: str) -> str:
    """Переводит гибридный .val в современную схему 0.6.8."""
    if not text.endswith("\n"):
        text += "\n"

    # 1. version -> 0.6.8
    text = re.sub(
        r"<version>\s*0\.6\.\d+\s*</version>",
        f"<version>{TARGET_VERSION}</version>",
        text,
    )

    # версия исходного файла (для legacy-решений ниже)
    mver = re.search(r"<version>\s*(?P<v>[0-9]+\.[0-9]+\.[0-9]+)", text)
    ver_parts = tuple(int(x) for x in (mver.group("v").split(".") if mver else ["0", "0", "0"]))

    # Файлы старее 0.6 не трогаем: в их схемах нет patternLabel/draftBlock и т.п.,
    # а сам Seamly 0.6.8 при открытии переконвертирует старый формат.
    # (legacy-файлы 0.2-0.5 с не-ASCII символами в запись см. probe-тесты.)
    if ver_parts < (0, 6, 0):
        return text

    # 2. ensure <patternLabel> exists (0.6+; в более старых схеме нет такого элемента)
    if "<patternLabel" not in text:
        label = (
            '\n    <patternLabel>\n        <line alignment="0" bold="false" '
            'italic="false" sfIncrement="0" text=""/>\n    </patternLabel>'
        )
        m = re.search(r"<notes\s*/?>", text)
        insert_after = None
        if m:
            if m.group(0).endswith("/>"):
                insert_after = m.end()
            else:
                close = "</notes>"
                c = text.find(close, m.end())
                insert_after = c + len(close) if c != -1 else None
        if insert_after is None:
            c = text.find("<measurements")
            if c == -1:
                raise ValueError("cannot locate insertion point for patternLabel")
            insert_after = c
        eol = text.find("\n", insert_after)
        if eol == -1:
            raise ValueError("no newline after insertion point")
        text = text[: eol + 1] + label + text[eol + 1:]

    # 3. <draw name="X"> -> <draftBlock name="X">
    text = re.sub(r'<draw\s+name="([^"]*)">', r'<draftBlock name="\1">', text)
    text = text.replace("</draw>", "</draftBlock>")

    # 4. remove showPointName attributes (points in old schema)
    text = re.sub(r'\s+showPointName="[^"]*"', "", text)

    # 4b. legacy intersection points: type pointOfIntersection -> intersectXY,
    #     drop the old pointOfIntersection attr, add line style/color/weight
    #     (mirrors VPatternConverter::toVersion0_6_4).
    text = re.sub(
        r'<point(?=[^>]*\btype="pointOfIntersection")[^>]*>',
        lambda m: re.sub(
            r'type="pointOfIntersection"',
            'type="intersectXY"',
            re.sub(r'\s+pointOfIntersection="[^"]*"', "", m.group(0)),
        ).replace(
            'type="intersectXY"',
            'lineColor="black" lineType="dashLine" lineWeight="0.35" type="intersectXY"',
        ),
        text,
    )

    # 5. <details> -> <pieces> (в т.ч. самозакрывающийся <details/>)
    text = text.replace("<details>\n", "<pieces>\n")
    text = text.replace("</details>\n", "</pieces>\n")
    text = text.replace("<details>", "<pieces>")
    text = text.replace("</details>", "</pieces>")
    text = text.replace("<details/>", "<pieces/>")

# 6. <detail ...> opening tags -> <piece closed="1" ...>; </detail> -> </piece>
    text = re.sub(
        r"<detail\b[^>]*>",
        lambda m: _convert_detail_opening(m.group(0)),
        text,
    )
    text = re.sub(r"</detail\s*>", "</piece>", text)

    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Конвертация .val гибридной схемы в modern 0.6.8 (draftBlock+pieces)."
    )
    parser.add_argument("src", help="исходный .val")
    parser.add_argument("dst", help="результирующий .val (0.6.8)")
    args = parser.parse_args()

    with open(args.src, "r", encoding="utf-8") as f:
        data = f.read()
    out = convert(data)
    with open(args.dst, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {args.dst} ({len(out)} bytes)")


if __name__ == "__main__":
    main()