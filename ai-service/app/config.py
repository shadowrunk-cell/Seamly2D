"""Загрузка конфигурации провайдеров LLM."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class ModelSpec(BaseModel):
    """Модель, привязанная к одной или нескольким ролям."""

    role: str
    name: str


class ProviderConfig(BaseModel):
    """Конфигурация одного провайдера LLM."""

    name: str
    type: str
    base_url: Optional[str] = None
    api_key_env: str = ""
    default_model: str = ""
    models: list[ModelSpec] = Field(default_factory=list)

    def get_api_key(self) -> Optional[str]:
        if not self.api_key_env:
            return None
        return os.environ.get(self.api_key_env)

    def get_model_for_role(self, role: str) -> Optional[str]:
        for m in self.models:
            if m.role == role:
                return m.name
        return None

    def has_role(self, role: str) -> bool:
        return self.get_model_for_role(role) is not None


class AppConfig(BaseModel):
    """Полная конфигурация AI-сервиса."""

    default_text_role: str = "gpt-4o"
    default_vision_role: str = "gpt-4o"
    providers: list[ProviderConfig] = Field(default_factory=list)

    def get_provider(self, role: str) -> Optional[ProviderConfig]:
        for p in self.providers:
            if p.has_role(role):
                return p
        return None


def load_config(path: Optional[Path] = None) -> AppConfig:
    """Загружает конфигурацию из providers.yaml (или пример из providers.example.yaml)."""
    cfg_path = path or PROJECT_ROOT / "providers.yaml"
    if not cfg_path.exists():
        cfg_path = PROJECT_ROOT / "providers.example.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    return AppConfig(**raw)


config = load_config()
