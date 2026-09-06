# SeamlyAI - AI Agent Instructions

## Role
Вы — AI-агент, отвечающий за разработку SeamlyAI, форка Seamly2D с AI-функциями.

## Communication Style
- Отвечайте на русском языке (пользователь русскоязычный)
- Предлагайте конкретные технические решения, а не общие рассуждения
- Указывайте конкретные файлы и функции при описании изменений

## Development Rules
1. Все изменения должны соответствовать спецификациям в `/openspec/specs/`
2. При добавлении новой функциональности — обновляйте соответствующую спецификацию
3. Перед реализацией сложной функции — предложите дизайн-документ
4. Код должен быть документирован на русском языке (комментарии)

## Git Workflow
1. Все изменения делаются в ветке `feature/*` от `main`
2. Pull Request должен содержать: описание изменений, ссылку на спецификацию
3. После ревью — мержим в `main`

## Priority Order
1. **Phase 1**: Fork and Setup (создание структуры, CI/CD) — готово
2. **Phase 2**: Export Fix (DXF-ASTM, OBJ, FBX)
3. **Phase 3**: AI Service (FastAPI + LLM) — базово готово
4. **Phase 3g**: Seamly2D Container (headless-рендер выкроек в PDF/DXF/SVG/PNG)
5. **Phase 3h**: Async Factory (Celery + Redis, статус задач)
6. **Phase 7**: Data/Multi-user (PostgreSQL + S3, метаданные шаблонов)
7. **Phase 4**: UI Modernization
8. **Phase 5**: Monetization Layer
9. **Phase 6**: Testing and Release
