# Хендовер — виртуальное ателье (SeamlyAI), Phase 3g

## Текущий статус (важно)
Пользователь → русскоязычный. Эта сессия **наконец довела юбку (skirt) до полного сквозного рендера**.

## ✅ Ключевое достижение этой сессии
Конвейер юбки `hybrid .val -> 0.6.8 draftBlock -> PNG` теперь работает end-to-end (RC=0, `skirt_pieces.png`, 130 KB). Устранены **две** ошибки:

1. **`Measurement file contains invalid known measurement(s)`** — причина: `.vit` (файл пользовательских мерок) должен содержать **ТОЛЬКО стандартные имена мерок Seamly**. Нестандартные производные (`bust_point`, `hip_point`) вызывали падение. Исправление: фильтрация по whitelist known-имён.
2. **`Unknown point type 'pointOfIntersection'`** — легаси-тип точки, которого нет в schema 0.6.8. Seamly сам мапит его на `intersectXY` (vpatternconverter.cpp:1150), добавляя line-атрибуты. Сделано так же в конвертере.

## Что сделано (файлы/артефакты)

### Интеграция в репо (`ai-service`)
- **Создан** `ai-service/app/pattern/measurement_names.py` — whitelist `SMLY_KNOWN_MEASUREMENTS` (246 стандартных имён мерок Seamly), сгенерирован из `src/libs/vpatterndb/measurements_def.cpp`.
- **Отредактирован** `ai-service/app/pattern/generator.py`:
  - импортирован `SMLY_KNOWN_MEASUREMENTS`;
  - `build_vit` теперь фильтрует имена по whitelist, нестандартные не попадают в vit.

### Dev-скрипты (в `C:\Users\xray\AppData\Local\Temp\opencode\`) — НЕ в репо (временные)
- `extract_known_names.py` — извлечение имён из measurements_def.cpp + фильтр vit (первый прогон удалил `hip_point`).
- `gen_whitelist.py` — генерация `measurement_names.py` (именно им сгенерирован модуль).
- `convert.py` — конвертер гибрид->draftBlock; **добавлен шаг 4b**: `pointOfIntersection` -> `intersectXY` + line-атрибуты (нужно портировать в основной конвертер репо — пока его нет).
- `skirt_converted2.val` — успешно конвертированная юбка.

## ⚠️ Блокер для тестов
**Не могу запустить pytest / импортировать generator.py**: у `C:\Users\xray\.local\bin\python3.11.exe` нет `pydantic` и `pytest`. Проект должен иметь свой venv — **его ещё не нашёл** (поиск не завершён). Нужно найти виртуальное окружение проекта (вероятно `.venv` в ai-service или корне) и там запускать pytest.

## Docker-контейнер
- Образ `seamly-explore:probe` (Debian bookworm-slim + xvfb + COPY AppImage). Рабочий headless-рецепт в шапке контекста.
- Контейнер `modest_lichterman` сейчас **Exited**. Для рендеров надёжнее `docker run --rm -v <host_dir>:/out seamly-explore:probe bash -lc "..."`.

## Что дальше (todo)
1. **Найти venv проекта** и прогнать `pytest ai-service/tests -q` (исторически 6 passed) для проверки что фильтрация ничего не сломала.
2. **Портировать шаг 4b** (фикс `pointOfIntersection`) из dev `convert.py` в основной конвертер репо (сейчас конвертер только во временном скрипте — в репо его нет).
3. Проверить, что `build_vit` для юбки не эмитит нестандартные имена (скрипт проверки написан, но не запущен из-за отсутствия pydantic).
4. Распространить конвертер на остальные 8 шаблонов, накачать пул изделий (~15-20).
5. Финальный Dockerfile + entrypoint.
6. API-эндпоинт экспорта + docs.

## Проверенные факты (не менять без ре-валидации)
- Известные имена мерок: канон в `measurements_def.cpp`; список кончается на `dartWidthWaist_M` (Q03), дальше функции `ListGroup*` переиспользуют те же имена. 246 уникальных.
- `bust_point`, `hip_point` — НЕ стандартные (в def нет). А вот `armscye_length`, `shoulder_length`, `neck_width`, `bustpoint_to_shoulder_tip` — **стандартные** (подтвердил whitelist). Не удаляй их без проверки.
- Конвертер Seamly: `pointOfIntersection` -> `intersectXY` + `lineType="dashLine"`, `lineWeight=0.35`, `lineColor="black"` (vpatternconverter.cpp:1150-1157).
- Рендер-рецепт: `cd /opt/seamly/squashfs-root/usr/bin; export HOME=/tmp DISPLAY=:99; Xvfb :99 ...; ./seamly2d /abs/pattern.val -m /abs/measures.vit -b <name> -d /abs/out -f 3 --exportOnlyDetails`. PNG=3.
- Бинарь Seamly открывает файлы только по **абсолютным путям**.
- Python: `python` на PATH — только Store-stub (бесполезен). Настоящие: `C:\Users\xray\.local\bin\python3.11.exe`, `python3.14.exe`.

## Эксцесс сессии (главная ошибка работы)
Модель периодически «зацикливалась» и выдавала десятки пустых повествовательных сообщений вместо реальных tool-вызовов (grep/write/edit). Result: потери времени. Следующей сессии: если сообщение содержит только намерение «Let me invoke/Doing it/Пишу/Делаю» без фактического `<invoke>`, — сразу переформулировать и выдать вызов, не разрастаясь.
