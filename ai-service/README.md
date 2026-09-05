# SeamlyAI — AI-сервис

Python/FastAPI микросервис с AI-функциями конструирования одежды.

## Возможности

- **Чат с LLM** (текст + vision прикреплённых эскизов) через абстракцию провайдеров
- **Генерация лекал** по шаблонам Seamly (VIT): базовый лиф, юбка, брюки
- **Провайдер-агностик**: сменные модели OpenAI-совместимые / Anthropic / Ollama
  без правки кода — только правка `providers.yaml`
- **Веб-интерфейс** чата на `/`

## Быстрый старт

```bash
# 1. Создать окружение
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить провайдеров (создать providers.yaml из примера)
cp providers.example.yaml providers.yaml
#    и заполнить нужные блоки. Как минимум один провайдер с ролью "text".

# 4. Запустить
uvicorn app.main:app --reload
```

Откройте http://localhost:8000 — веб-чат. Документация API: http://localhost:8000/docs

## Конфигурация провайдеров

Принцип: **привязка не железная**. Модели меняются в `providers.yaml` без пересборки.

Роли моделей:
- `text` — основная языковая модель
- `vision` — модель со зрением
- `image` — (опц.) генерация картинок

Одна модель может закрывать несколько ролей (например, Claude — text и vision).
Подробнее см. комментарии в `providers.example.yaml`.

**Важно:** `providers.yaml` содержит ключи — не коммитьте его (в `.gitignore`).

## API

| Метод | Путь | Назначение |
|-------|------|-----------|
| GET  | `/health` | Проверка здоровья |
| GET  | `/api/providers` | Список провайдеров и моделей |
| GET  | `/api/patterns/templates` | Доступные шаблоны и нужные мерки |
| POST | `/api/patterns` | Генерация лекала по шаблону и меркам |
| POST | `/api/patterns/download` | Генерация и отдача `.val` как файла |
| POST | `/api/patterns/render` | Рендер лекала в PNG через headless Seamly2D (требует Docker) |
| POST | `/api/chat` | Чат с LLM (текст + опц. картинка) |

## Рендер в PNG (требует Docker)

`POST /api/patterns/render` генерирует `.val` (modern 0.6.8) и `.vit` из запроса,
запускает headless-рендер в контейнере `seamly-renderer:latest` и возвращает PNG.

Собрать образ рендера:
```bash
docker build -t seamly-renderer:latest ai-service/seamly-renderer
```

Ошибки:
- `503 RenderUnavailable` — нет Docker/демона;
- `422 RenderError` — контейнер не дал PNG (например, «empty scene» — в шаблоне нет деталей).

## Структура

```
ai-service/
├─ app/
│  ├─ main.py                 # FastAPI точка входа
│  ├─ config.py               # загрузка providers.yaml
│  ├─ providers/              # адаптеры LLM (openai_compat, anthropic)
│  ├─ pattern/                # генерация лекал (шаблоны, мерки, конвертер, рендер)
│  ├─ routes/                 # API-маршруты
│  └─ static/index.html       # веб-чат
├─ templates/                 # шаблоны .val (гибридная схема <draw>+<details>)
├─ tests/                     # тесты (без LLM; рендер мокается)
├─ scripts/build_pool.py      # конвертация всех шаблонов в 0.6.8 + генерация мерок
├─ seamly-renderer/           # Docker-образ headless рендера (Dockerfile, AppImage, скрипты)
├─ providers.example.yaml
└─ requirements.txt
```

## Тесты

```bash
python -m pytest tests -q     # 21 тест
```

## Шаблоны лекал

Шаблоны получены из проекта [darrenstarr/Patterns](https://github.com/darrenstarr/Patterns)
(лицензия автора). Каждый шаблон требует определённый набор мерок; недостающие
вычисляются из базовых (ОГ/ОТ/ОБ — обхват груди/талии/бёдер, и рост) пропорций типовой фигуры.

| Шаблон | Ключ | Источник |
|--------|------|----------|
| Базовый лиф | `bodice` | Darragh Starr / Bodice_Exact |
| Базовая юбка | `skirt` | TheShapesOfFabric / basic skirt block |
| Базовые брюки | `trousers` | TheShapesOfFabric / basic trouser block |
