# Хендовер — виртуальное ателье (SeamlyAI), Phase 3i

## Статус
Сессия 3g→3h завершила конвейер render (14 OK/4 EMPTY/0 FAIL, 21 тест, коммит `d188370ba5`).
Сессия 3i добавила **async factory + форматы вывода + UI-экспорт**. Redis живёт: `docker run -d --name seamly-redis -p 6379:6379 redis:7-alpine`.

## Сделано в 3i
1. **Async job queue (Celery + Redis)** — спека `openspec/specs/async-generation/`:
   - `ai-service/app/tasks.py` — Celery-приложение + задача `patterns.render`;
   - `ai-service/app/asyncq.py` — фасад submit/get/download; **gracefallback**:
     если Redis недоступен, задачи исполняются локальными потоками (dev/тесты);
   - маршруты: `POST /api/patterns/jobs`, `GET /jobs/{id}`, `GET /jobs/{id}/result`;
   - транзиентные сбои рендера → `self.retry` с backoff (авто-reitry до 3);
   - проверено E2E с реальным Redis+Celery+Docker: PENDING→SUCCESS, PNG скачан.
2. **Форматы вывода** — специф-карта Seamly2D: SVG=0, PDF=1, PDF-tiled=2, PNG=3, JPG=4, DXF(2010)=17, DXF-AAMA=19.
   - `render_one.sh [val] [vit] [base] [format]` (параметр + проверка расширения);
   - `render.py` → `FORMATS` + `RenderResult.file_path` (было `png_path`);
   - `routes`: `/render?format=`, `/jobs?format=`; swagger на `/docs`;
   - проверено реально: SVG/PDF/DXF рендерятся (по отдельности; параллельные
     контейнеры иногда дают SIGABRT — флаке, повтор проходит).
3. **UI-экспорт** (`ai-service/app/static/index.html`):
   - панель мерок → блок «Скачать»: выбор формата PNG/SVG/PDF/DXF/.val;
   - `exportBtn` вызывает `/render?format=` (или `/download` для .val) и сохраняет файл;
   - ход рендера показывается в подсказке.

## Новые/изменённые файлы
- NEW `ai-service/app/tasks.py`, `ai-service/app/asyncq.py`, `ai-service/tests/test_asyncq.py`
- M `ai-service/app/pattern/render.py`, `ai-service/seamly-renderer/render_one.sh`,
  `ai-service/app/routes/patterns.py`, `ai-service/tests/test_render.py`,
  `ai-service/requirements.txt` (+celery, redis), `.gitignore`
- M `ai-service/app/static/index.html`, `ai-service/README.md`

## Пометки / подводные камни
- **Тесты: 28 passed** (pytest `ai-service/tests -q`).
- Коммит НЕ делался в 3i (запрос пользователя). Следующий шаг — команда коммита.
- `worker`: `celery -A app.tasks.celery_app worker --loglevel=info --pool=solo` (Windows solo).
- Параллельные docker-рендеры (2+ контейнера одновременно) иногда роняют Seamly2D (SIGABRT).
- Template Metadata Store из спеки не реализован (это Phase 7: PostgreSQL + S3) — остаётся открытым.
- Процессы, оставшиеся запущенными на машине: uvicorn :8000, celery worker, redis («seamly-redis»).

## Не коммитить (gitignored)
`seamly-renderer/render_out/`, `seamly-renderer/async_out/`, `seamly-renderer/fmt_test/`,
`ai-service/seamly-renderer/*.AppImage`, `.venv`, `providers.yaml`.