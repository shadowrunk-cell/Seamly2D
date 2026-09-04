# Design: SeamlyAI Architecture

## Architectural Decisions

### 1. Fork Strategy
- **Decision**: Форкнуть Seamly2D, а не Valentina
- **Reason**: Seamly2D имеет более активное сообщество и открыто заявляет о намерении двигаться в сторону 3D

### 2. AI Integration Architecture
- **Decision**: Вынести AI-логику в отдельный микросервис на Python/FastAPI
- **Reason**:
  - Независимость от основного C++ кода
  - Легче экспериментировать с разными LLM
  - Возможность развернуть как облачный сервис для монетизации

### 3. Export Fix Strategy
- **Problem**: Seamly2D экспортирует кривые как множество мелких отрезков, что ломает работу в CLO 3D
- **Solution**: Реализовать генерацию корректного DXF-ASTM с маркировкой точек кривых (spline-информация)

### 4. UI Modernization
- **Decision**: Использовать Qt Quick/QML для переработки интерфейса
- **Alternative**: Electron + React (если делать веб-версию)
- **Reason**: Qt Quick позволяет сохранить производительность нативного приложения с современным дизайном

### 5. Monetization Architecture
- **Freemium Model**:
  - Бесплатно: Базовое конструирование, локальный AI (ограниченный), экспорт в базовые форматы
  - Платно: Cloud AI (неограниченный), приоритетный экспорт, командная работа, облачное хранилище
