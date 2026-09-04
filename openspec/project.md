# SeamlyAI — AI-ориентированная САПР для конструирования одежды

## Project Purpose
Создание форка Seamly2D с интеграцией AI-функций, улучшенным UX и бесшовной интеграцией с 3D-пакетами (CLO 3D, Blender). Целевая аудитория: независимые дизайнеры, малые ателье, энтузиасты.

## Core Principles
1. **Инженерная точность** — использование проверенной параметрической базы Seamly2D
2. **AI-ассистент** — автоматизация рутинных задач, генерация лекал по эскизу
3. **Бесшовная интеграция** — корректный экспорт в форматы, понятные CLO 3D и Blender
4. **Современный UX** — интерфейс в стиле Figma/современных дизайн-инструментов
5. **Доступность** — Freemium-модель с открытым ядром

## Technology Stack
- **Core**: C++/Qt (наследуется от Seamly2D); форматы `.val`/`.sm2d`/`.vit`
- **AI Layer**: Python FastAPI микросервис + интеграция с LLM (провайдер-агностик: OpenCode,
  локальные модели, Сбер/GigaChat, Ollama, Azure, vLLM)
- **Async (целевая схема)**: Celery + Redis (очередь длительных задач рендера выкроек)
- **Storage (целевая схема)**: PostgreSQL (пользователи, заказы, метаданные шаблонов) +
  объектное хранилище S3 (файлы шаблонов и готовых выкроек) при масштабировании
- **Frontend (опционально для веб-версии)**: React/TypeScript
- **3D Integration**: Экспорт в DXF-ASTM, OBJ, FBX
- **Rendering**: Docker-контейнер с headless-Seamly2D (пакетный экспорт в PDF/DXF/SVG/PNG)
- **Deployment**: Electron для десктоп-версии, Docker Compose для backend-сервисов

## Phases
1. **Phase 1 — Fork and Setup** (готово): форк, CI/CD, rename, OpenSpec
2. **Phase 2 — Export Fix** (план): гарантированный экспорт в DXF/гладалэк
3. **Phase 3 — AI Service** (готово): FastAPI + LLM + генерация лекал + каталог изделий
4. **Phase 3g — Seamly2D Container** (план): headless-рендер выкроек в PDF/DXF/SVG/PNG
5. **Phase 3h — Async Factory** (план): Celery + Redis, статус задач по `job_id`
6. **Phase 7 — Data/Multi-user** (план): PostgreSQL + S3, метаданные шаблонов из БД
7. **Phase 4 — UI Modernization** (план): React/TS приложение
8. **Phase 5 — Monetization** (план): Freemium
9. **Phase 6 — Testing and Release** (план)
