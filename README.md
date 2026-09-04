# SeamlyAI — AI-ориентированная САПР для конструирования одежды

[![CI/CD](https://github.com/shadowrunk-cell/Seamly2D/actions/workflows/ci.yml/badge.svg)](https://github.com/shadowrunk-cell/Seamly2D/actions/workflows/ci.yml)

SeamlyAI — это форк [Seamly2D](https://github.com/FashionFreedom/Seamly2D) с интеграцией AI-функций, улучшенным UX и бесшовной интеграцией с 3D-пакетами (CLO 3D, Blender). Целевая аудитория: независимые дизайнеры, малые ателье, энтузиасты.

## Core Principles

1. **Инженерная точность** — использование проверенной параметрической базы Seamly2D
2. **AI-ассистент** — автоматизация рутинных задач, генерация лекал по эскизу
3. **Бесшовная интеграция** — корректный экспорт в форматы, понятные CLO 3D и Blender
4. **Современный UX** — интерфейс в стиле Figma/современных дизайн-инструментов
5. **Доступность** — Freemium-модель с открытым ядром

## Technology Stack

- **Core**: C++/Qt (наследуется от Seamly2D)
- **AI Layer**: Python FastAPI микросервис + интеграция с LLM (Claude/Codex)
- **Frontend (опционально для веб-версии)**: React/TypeScript
- **3D Integration**: Экспорт в DXF-ASTM, OBJ, FBX
- **Deployment**: Electron для десктоп-версии, Docker для backend-сервисов

## Дорожная карта (Phases)

| Phase | Описание |
|-------|----------|
| 1 | Fork & Setup (создание структуры, CI/CD) |
| 2 | Export Fix (DXF-ASTM, OBJ, FBX) |
| 3 | AI Service (FastAPI + LLM) |
| 4 | UI Modernization |
| 5 | Monetization Layer |
| 6 | Testing & Release |

Подробные спецификации и задачи находятся в каталоге [`openspec/`](openspec/).

## Сборка

### Требования

- Qt 6 (base, declarative, svg, script, tools)
- CMake 3.16+ или qmake
- C++17 компилятор
- Eigen3, Boost

### Linux (Fedora)

```bash
sudo dnf install -y gcc-c++ cmake make ninja-build \
  qt6-qtbase-devel qt6-qtdeclarative-devel qt6-qtsvg-devel \
  qt6-qtscript-devel qt6-qttools-devel eigen3-devel boost-devel libGL-devel

cmake -S . -B build -G Ninja -DCMAKE_PREFIX_PATH=/usr/lib64/qt6
cmake --build build --parallel
```

### Windows

```powershell
git clone https://github.com/shadowrunk-cell/Seamly2D.git
# Откройте Seamly2D.pro в Qt Creator и соберите проект
```

## Лицензия

Проект распространяется под лицензией GPL-3.0 (см. [`LICENSE.md`](LICENSE.md)).

## Разработка

Инструкции для AI-агентов: [`openspec/AGENTS.md`](openspec/AGENTS.md).
