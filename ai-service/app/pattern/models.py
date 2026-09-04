"""Pydantic-модели для паттернов и мерок."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

MeasurementType = Literal["bust", "waist", "hip", "waist_to_hip", "height", "other"]


class MeasurementInput(BaseModel):
    """Одна введённая пользователем мерка."""

    name: str = Field(description="Имя мерки (например 'bust_circ')")
    value: float = Field(description="Значение в см")
    unit: Literal["cm", "mm", "inch"] = "cm"


class MeasurementsRequest(BaseModel):
    """Мерки пользователя для построения лекала."""

    measurements: list[MeasurementInput]
    size: Optional[str] = Field(default=None, description="Стандартный размер, напр. 'Size 10'")


class PatternRequest(BaseModel):
    """Запрос на генерацию паттерна."""

    template: Literal["bodice", "skirt", "trousers"]
    measurements: list[MeasurementInput] = Field(default_factory=list)
    size: Optional[str] = None
    adjustments: dict[str, float] = Field(
        default_factory=dict, description="Корректировки инкрементов, напр. {'#skirt_length': 60}"
    )
    output_format: Literal["val", "vit"] = "val"

    @property
    def to_cm(self) -> dict[str, float]:
        return {m.name: m.value for m in self.measurements}


class PatternResponse(BaseModel):
    """Результат генерации паттерна."""

    filename: str
    content: str = Field(description="Содержимое файла .val (VIT)")
    template: str
    applied_measurements: dict[str, float]
    missing_measurements: list[str] = Field(
        default_factory=list, description="Мерки шаблона, не покрытые пользователем"
    )
    warnings: list[str] = Field(default_factory=list)
