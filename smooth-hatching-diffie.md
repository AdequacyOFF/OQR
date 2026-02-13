# План реализации: Веб-приложение для контроля проведения олимпиады

## Контекст

Разрабатывается полное веб-приложение для управления олимпиадами с анонимными QR-кодами. Система обеспечивает:
- Регистрацию участников и выдачу входных QR-кодов
- Допуск через сканирование QR (одноразовое использование)
- Генерацию анонимных бланков с QR-кодами
- OCR распознавание итоговых баллов из сканов
- Публикацию результатов

**Критические требования безопасности:**
- QR-коды содержат только криптографически стойкие токены (128+ бит энтропии)
- В БД хранятся только HMAC-SHA256 хэши токенов, никогда исходные значения
- По QR невозможно определить участника без доступа к серверу
- Все изменения статусов логируются в audit_log

**Текущее состояние:** Новый проект, есть только Poetry конфигурация (Python 3.13) и виртуальное окружение.

**Объем работы:** Полная реализация Backend + Frontend + Docker + CI/CD + OCR функциональность.

---

## Архитектурные решения

### Backend: Clean Architecture
Четырехслойная архитектура для разделения concerns и тестируемости:

1. **Domain Layer** (`backend/src/olimpqr/domain/`)
   - Entities: User, Participant, Competition, Registration, EntryToken, Attempt, Scan, AuditLog
   - Value Objects: Token, TokenHash, Score, UserRole
   - Domain Services: TokenService (HMAC генерация/проверка), QRService
   - Repository интерфейсы (абстракции)

2. **Application Layer** (`backend/src/olimpqr/application/`)
   - Use Cases: RegisterUser, VerifyEntryQR, GenerateAnswerSheet, ProcessScanOCR, ApplyScore, PublishResults
   - DTOs для передачи данных
   - Интерфейсы для Infrastructure (OCRService, PDFService, StorageService)

3. **Infrastructure Layer** (`backend/src/olimpqr/infrastructure/`)
   - SQLAlchemy модели и репозитории (PostgreSQL)
   - MinIO storage для PDF и сканов
   - PaddleOCR + OpenCV для распознавания баллов
   - ReportLab для генерации PDF бланков
   - Celery tasks для асинхронной обработки OCR
   - JWT/bcrypt для безопасности

4. **Presentation Layer** (`backend/src/olimpqr/presentation/`)
   - FastAPI эндпоинты для всех ролей
   - Pydantic schemas (request/response)
   - Middleware (CORS, error handling, logging)
   - Dependencies (JWT auth, role checks, DB sessions)

### Frontend: React + TypeScript
- **React Router** для навигации по ролям (Participant, Admitter, Scanner, Admin)
- **Zustand** для state management (легковеснее Redux)
- **Axios** клиент с JWT interceptors
- **html5-qrcode** для сканирования QR через камеру
- **qrcode.react** для отображения QR-кодов
- **Vite** для быстрой разработки

### Docker Infrastructure
- PostgreSQL 16 (основная БД с enum типами для статусов)
- Redis 7 (брокер для Celery)
- MinIO (S3-compatible хранилище файлов)
- Backend (FastAPI + Uvicorn)
- Celery Worker (обработка OCR)
- Frontend (nginx static server)

---

## Структура проекта

```
OlimpQR/
├── backend/
│   ├── src/olimpqr/
│   │   ├── domain/              # Бизнес-логика
│   │   │   ├── entities/        # User, Competition, Attempt, Scan
│   │   │   ├── value_objects/   # Token, Score, UserRole
│   │   │   ├── services/        # TokenService, QRService
│   │   │   └── repositories/    # Интерфейсы репозиториев
│   │   ├── application/         # Use Cases
│   │   │   ├── use_cases/       # RegisterUser, VerifyQR, ProcessOCR
│   │   │   ├── dto/             # Data Transfer Objects
│   │   │   └── interfaces/      # OCRService, PDFService, StorageService
│   │   ├── infrastructure/      # Реализации
│   │   │   ├── database/        # SQLAlchemy модели + репозитории
│   │   │   ├── ocr/             # PaddleOCR + OpenCV
│   │   │   ├── pdf/             # ReportLab генератор бланков
│   │   │   ├── storage/         # MinIO клиент
│   │   │   ├── tasks/           # Celery tasks
│   │   │   └── security/        # JWT, password hashing
│   │   └── presentation/        # API Layer
│   │       ├── api/v1/          # FastAPI endpoints по ролям
│   │       ├── dependencies/    # Auth, DB session
│   │       └── schemas/         # Pydantic модели
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Unit/Integration/E2E тесты
│   └── pyproject.toml           # Poetry зависимости
│
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios API клиент
│   │   ├── components/          # React компоненты
│   │   │   ├── common/          # Button, Input, Modal
│   │   │   ├── layout/          # Header, Sidebar
│   │   │   └── qr/              # QRScanner, QRCodeDisplay
│   │   ├── pages/               # Страницы по ролям
│   │   │   ├── auth/            # Login, Register
│   │   │   ├── participant/     # Dashboard, EntryQR
│   │   │   ├── admitter/        # QRScannerPage, PrintSheet
│   │   │   ├── scanner/         # UploadScan, VerifyScore
│   │   │   └── admin/           # Competitions, Users, AuditLog
│   │   ├── store/               # Zustand state
│   │   ├── router/              # React Router config
│   │   └── types/               # TypeScript types
│   ├── package.json
│   └── vite.config.ts
│
├── docker/                      # Dockerfiles
│   ├── backend/Dockerfile
│   ├── frontend/Dockerfile
│   └── celery/Dockerfile
│
├── docker-compose.yml           # Все сервисы
├── .gitlab-ci.yml              # CI/CD pipeline
└── .env.example                 # Переменные окружения
```

---

## Модель данных (ключевые таблицы)

### users
- id (UUID), email (unique), password_hash, role (enum), is_active

### participants
- id (UUID), user_id (FK → users), full_name, school, grade

### competitions
- id (UUID), name, date, registration_start/end, variants_count, max_score, status (enum)
- Статусы: DRAFT, REGISTRATION_OPEN, IN_PROGRESS, CHECKING, PUBLISHED

### registrations
- id (UUID), participant_id (FK), competition_id (FK), status (enum)
- UNIQUE(participant_id, competition_id) - один участник = одна регистрация

### entry_tokens (входные QR)
- id (UUID), **token_hash (HMAC-SHA256, unique)**, registration_id (FK), expires_at, used_at
- Хранится только hash, исходный токен только в QR коде

### attempts (бланки)
- id (UUID), registration_id (FK), variant_number, **sheet_token_hash (unique)**, status (enum), score_total, confidence
- Статусы: PRINTED, SCANNED, SCORED, PUBLISHED, INVALIDATED

### scans (загруженные сканы)
- id (UUID), attempt_id (FK), file_path (MinIO), ocr_score, ocr_confidence, verified_by (FK → users)

### audit_log (полное логирование)
- id (UUID), entity_type, entity_id, action, user_id (FK), ip_address, details (JSONB), timestamp

**Ключевые индексы:**
- entry_tokens.token_hash, attempts.sheet_token_hash (поиск по QR)
- attempts.status, competitions.status (фильтрация по статусам)
- audit_log(entity_type, entity_id), audit_log(timestamp DESC)

---

## Критические компоненты

### 1. TokenService (backend/src/olimpqr/domain/services/token_service.py)
**Назначение:** Ядро безопасности - генерация и проверка токенов.

```python
class TokenService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')

    def generate_token(self) -> Token:
        """Генерирует токен (256 бит энтропии) + HMAC-SHA256 hash"""
        raw_token = secrets.token_urlsafe(32)  # 256 бит
        token_hash = self._compute_hash(raw_token)
        return Token(raw=raw_token, hash=token_hash)

    def verify_token(self, raw_token: str, stored_hash: str) -> bool:
        """Constant-time сравнение для защиты от timing attacks"""
        computed_hash = self._compute_hash(raw_token)
        return hmac.compare_digest(computed_hash, stored_hash)
```

**Важно:** Исходный токен возвращается только при генерации, далее нигде не хранится.

### 2. PaddleOCRService (backend/src/olimpqr/infrastructure/ocr/paddle_ocr.py)
**Назначение:** Распознавание итогового балла из фиксированной области бланка.

Процесс:
1. Загрузить изображение скана
2. Вырезать область "Итоговый балл" (фиксированные координаты)
3. Предобработка: grayscale → CLAHE (контраст) → бинаризация Otsu
4. PaddleOCR распознавание
5. Извлечение числа regex
6. Возврат: score, confidence, raw_text

**Критично:** Поле балла на бланке должно быть в строго фиксированной области с оптимизацией под OCR (контраст, рамка, крупный шрифт).

### 3. SheetGenerator (backend/src/olimpqr/infrastructure/pdf/sheet_generator.py)
**Назначение:** Генерация PDF бланков с QR и полями.

PDF содержит:
- Заголовок: название соревнования, номер варианта
- **QR код** (sheet_token) - крупный, высокого качества
- **Поле "Итоговый балл"** в фиксированной области (x=150mm, y=250mm, w=40mm, h=15mm)
  - Жирная рамка
  - Крупный шрифт Courier-Bold 24pt для цифр
- Поля для ответов (нумерованные линии)

**Критично:** Координаты области балла должны совпадать в SheetGenerator и PaddleOCRService.

### 4. VerifyEntryQRUseCase (backend/src/olimpqr/application/use_cases/admission/verify_entry_qr.py)
**Назначение:** Проверка входного QR кода при допуске.

Процесс:
1. Вычислить hash токена из QR
2. Найти entry_token в БД по hash
3. Проверить срок действия (expires_at)
4. Проверить, не использован ли (used_at == NULL)
5. Вернуть данные регистрации (participant, competition)

**Важно:** При успешной проверке токен помечается used_at = NOW() → одноразовое использование.

### 5. ProcessScanOCR (Celery task, backend/src/olimpqr/infrastructure/tasks/ocr_tasks.py)
**Назначение:** Асинхронная обработка скана.

Процесс:
1. Скачать файл из MinIO
2. Извлечь QR код → получить sheet_token → найти Attempt
3. Вырезать область балла
4. Запустить OCR
5. Если confidence ≥ 0.7 → автоматически применить балл (status = SCORED)
6. Если confidence < 0.7 → требуется ручная проверка (status = SCANNED)

**Критично:** Celery worker должен иметь доступ к PaddleOCR моделям (контейнер с GPU опционально).

### 6. Auth Dependencies (backend/src/olimpqr/presentation/dependencies/auth.py)
**Назначение:** JWT проверка + разделение по ролям.

```python
def require_role(*allowed_roles: UserRole):
    async def dependency(token: str = Depends(oauth2_scheme)):
        user = verify_jwt_token(token)
        if user.role not in allowed_roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return dependency
```

Использование:
```python
@router.post("/admission/verify")
async def verify_qr(current_user = Depends(require_role(UserRole.ADMITTER))):
    ...
```

### 7. QRScanner Component (frontend/src/components/qr/QRScanner.tsx)
**Назначение:** Сканирование QR через веб-камеру (Admitter роль).

Использует **html5-qrcode** библиотеку:
- Запуск камеры (facingMode: 'environment' для задней камеры на мобильных)
- Continuous scanning (fps: 10)
- Callback при успешном декодировании → отправка на backend

---

## План реализации (10 недель)

### Фаза 1: Backend Foundation (Недели 1-2)
**Этапы 1-3:**
1. ✅ Настроить Docker (PostgreSQL, Redis, MinIO)
2. ✅ Создать SQLAlchemy модели + Alembic миграции
3. ✅ Реализовать Domain Layer (entities, TokenService, repositories)
4. ✅ Реализовать Infrastructure repositories (SQLAlchemy)
5. ✅ Unit тесты для domain логики

**Критерии:** БД запущена, миграции применяются, TokenService генерирует/проверяет токены.

### Фаза 2: Auth & Core API (Недели 2-3)
**Этапы 4-5:**
1. ✅ Реализовать Auth use cases (register, login)
2. ✅ JWT токены + password hashing (bcrypt)
3. ✅ FastAPI endpoints для auth
4. ✅ Competitions CRUD (admin, participant)
5. ✅ Dependencies для auth (JWT + role checks)

**Критерии:** Регистрация/логин работают, JWT проверяется, competitions API доступны.

### Фаза 3: Participant & Admitter Flows (Недели 3-4)
**Этапы 6-7:**
1. ✅ Registration use case (участник → соревнование)
2. ✅ Generate entry QR (entry_token)
3. ✅ Verify entry QR use case (Admitter сканирует)
4. ✅ Generate answer sheet use case (PDF + sheet_token)
5. ✅ PDF generator (ReportLab) с фиксированной областью балла
6. ✅ MinIO integration для хранения PDF

**Критерии:** Участник получает entry QR → Admitter сканирует → бланк генерируется с sheet QR.

### Фаза 4: OCR Infrastructure (Недели 4-5)
**Этапы 8-9:**
1. ✅ Настроить PaddleOCR + OpenCV
2. ✅ Реализовать image preprocessing
3. ✅ OCR service (извлечение балла из области)
4. ✅ QR extraction from scans
5. ✅ Celery configuration + Redis broker
6. ✅ Celery task: process_scan_ocr
7. ✅ Scanner API endpoints (upload, verify)

**Критерии:** Скан загружается → Celery обрабатывает → OCR извлекает балл → confidence проверяется.

### Фаза 5: Admin & Audit (Недели 5-6)
**Этапы 10:**
1. ✅ Admin CRUD endpoints (competitions, users)
2. ✅ Publish results use case
3. ✅ AuditLog middleware (логирование всех изменений)
4. ✅ Rate limiting (slowapi)
5. ✅ Public results page API

**Критерии:** Admin управляет системой, все действия логируются, результаты публикуются.

### Фаза 6: Frontend Infrastructure (Недели 6-7)
**Этапы 11-12:**
1. ✅ React + Vite setup
2. ✅ React Router (routes по ролям)
3. ✅ Axios client (JWT interceptors)
4. ✅ Zustand stores (auth, competitions)
5. ✅ Common components (Button, Input, Modal)
6. ✅ Auth pages (Login, Register)
7. ✅ Public pages (CompetitionsList, Results)

**Критерии:** Frontend запускается, логин работает, JWT хранится, роутинг по ролям.

### Фаза 7: Role-specific UI (Недели 7-8)
**Этапы 13-15:**
1. ✅ Participant UI (dashboard, entry QR display)
2. ✅ Admitter UI (QR scanner, admission, print sheet)
3. ✅ Scanner UI (upload scan, scan list, verify score)
4. ✅ QRScanner component (html5-qrcode)
5. ✅ QRCodeDisplay component

**Критерии:** Все роли имеют функциональные интерфейсы для своих задач.

### Фаза 8: Admin UI (Неделя 8-9)
**Этап 16:**
1. ✅ Admin dashboard
2. ✅ Competitions management (CRUD)
3. ✅ Users management (CRUD)
4. ✅ Audit log viewer (фильтры, поиск)
5. ✅ Publish results UI

**Критерии:** Admin может управлять всей системой через UI.

### Фаза 9: Docker Production & CI/CD (Неделя 9)
**Этапы 17-18:**
1. ✅ Production Dockerfiles (multi-stage builds)
2. ✅ nginx configuration для frontend
3. ✅ docker-compose.prod.yml
4. ✅ Health checks для всех сервисов
5. ✅ GitLab CI pipeline (lint, test, build, deploy)
6. ✅ Staging auto-deploy, production manual

**Критерии:** Production контейнеры запускаются, CI pipeline работает, staging деплоится автоматически.

### Фаза 10: Testing & Launch (Неделя 10)
**Этапы 19-20:**
1. ✅ E2E testing всех workflows
2. ✅ Нагрузочное тестирование (1000+ участников)
3. ✅ Security audit (токены, SQL injection, XSS)
4. ✅ Bug fixing
5. ✅ Performance optimization
6. ✅ Documentation (README, API docs, user guides)
7. ✅ Production deployment

**Критерии приемки:**
- ✅ Невозможно угадать валидный token
- ✅ По QR невозможно определить участника без БД
- ✅ Повторное использование entry_token невозможно
- ✅ OCR распознает ≥95% печатных баллов
- ✅ Все операции в audit_log
- ✅ Публичная страница результатов работает

---

## Технологический стек

### Backend
- **Python 3.13** + **Poetry**
- **FastAPI** (async web framework)
- **PostgreSQL 16** (БД с enum types)
- **SQLAlchemy 2.0** (ORM, async)
- **Alembic** (миграции)
- **Celery** + **Redis** (очередь задач)
- **MinIO** (S3-compatible storage)
- **PaddleOCR** + **OpenCV** (распознавание текста)
- **ReportLab** (генерация PDF)
- **PyJWT** (токены)
- **bcrypt** (пароли)

### Frontend
- **React 18** + **TypeScript**
- **Vite** (сборщик)
- **React Router 6** (навигация)
- **Zustand** (state management)
- **Axios** (HTTP клиент)
- **html5-qrcode** (сканирование QR)
- **qrcode.react** (отображение QR)
- **React Hook Form** + **Zod** (валидация форм)

### Infrastructure
- **Docker** + **docker-compose**
- **nginx** (frontend static)
- **GitLab CI/CD**

---

## Зависимости

### pyproject.toml (ключевые)
```toml
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.30.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.35"}
asyncpg = "^0.30.0"
alembic = "^1.13.0"
python-jose = {extras = ["cryptography"], version = "^3.3.0"}
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
minio = "^7.2.0"
celery = {extras = ["redis"], version = "^5.4.0"}
redis = "^5.2.0"
paddleocr = "^2.8.1"
opencv-python = "^4.10.0"
reportlab = "^4.2.0"
qrcode = {extras = ["pil"], version = "^8.0"}
slowapi = "^0.1.9"

# Dev
pytest = "^8.3.0"
pytest-asyncio = "^0.24.0"
ruff = "^0.7.0"
mypy = "^1.13.0"
```

### package.json (ключевые)
```json
"dependencies": {
  "react": "^18.3.1",
  "react-router-dom": "^6.26.0",
  "axios": "^1.7.0",
  "zustand": "^5.0.0",
  "html5-qrcode": "^2.3.8",
  "qrcode.react": "^4.1.0",
  "react-hook-form": "^7.53.0",
  "zod": "^3.23.0"
}
```

---

## Файлы для создания (приоритет)

### Высокий приоритет (Foundation)
1. `backend/pyproject.toml` - Обновить зависимости
2. `backend/src/olimpqr/config.py` - Конфигурация (pydantic-settings)
3. `backend/src/olimpqr/domain/services/token_service.py` - Ядро безопасности
4. `backend/src/olimpqr/infrastructure/database/models/*.py` - SQLAlchemy модели (9 файлов)
5. `backend/alembic/versions/001_initial_schema.py` - Первая миграция
6. `docker-compose.yml` - Инфраструктура
7. `.env.example` - Шаблон переменных окружения

### Средний приоритет (Business Logic)
8. `backend/src/olimpqr/domain/entities/*.py` - Domain entities (8 файлов)
9. `backend/src/olimpqr/application/use_cases/**/*.py` - Use cases (~15 файлов)
10. `backend/src/olimpqr/infrastructure/repositories/*.py` - Репозитории (5 файлов)
11. `backend/src/olimpqr/infrastructure/ocr/paddle_ocr.py` - OCR сервис
12. `backend/src/olimpqr/infrastructure/pdf/sheet_generator.py` - PDF генератор
13. `backend/src/olimpqr/infrastructure/storage/minio_storage.py` - MinIO клиент
14. `backend/src/olimpqr/infrastructure/tasks/ocr_tasks.py` - Celery tasks

### Средний приоритет (API)
15. `backend/src/olimpqr/main.py` - FastAPI приложение
16. `backend/src/olimpqr/presentation/api/v1/*.py` - API endpoints (6 файлов)
17. `backend/src/olimpqr/presentation/dependencies/auth.py` - Auth dependencies
18. `backend/src/olimpqr/presentation/schemas/*.py` - Pydantic schemas (6 файлов)

### Средний приоритет (Frontend Core)
19. `frontend/package.json` - Зависимости
20. `frontend/vite.config.ts` - Vite конфигурация
21. `frontend/src/main.tsx` - Точка входа
22. `frontend/src/router/routes.tsx` - Роутинг
23. `frontend/src/api/client.ts` - Axios клиент с JWT
24. `frontend/src/store/authStore.ts` - Auth state

### Низкий приоритет (Frontend UI)
25. `frontend/src/components/**/*.tsx` - Компоненты (~30 файлов)
26. `frontend/src/pages/**/*.tsx` - Страницы (~20 файлов)

### Низкий приоритет (Infrastructure)
27. `docker/backend/Dockerfile` - Backend образ
28. `docker/frontend/Dockerfile` - Frontend образ
29. `docker/celery/Dockerfile` - Celery worker образ
30. `.gitlab-ci.yml` - CI/CD pipeline

---

## Верификация (как проверить, что всё работает)

### 1. Docker контейнеры запускаются
```bash
docker-compose up -d
docker-compose ps  # Все сервисы в статусе "Up"
```

### 2. БД миграции применяются
```bash
docker-compose exec backend alembic upgrade head
# Проверить таблицы в PostgreSQL
docker-compose exec postgres psql -U olimpqr_user -d olimpqr -c "\dt"
```

### 3. Backend API доступен
```bash
curl http://localhost:8000/docs  # Swagger UI
curl http://localhost:8000/api/v1/competitions  # Пустой список
```

### 4. Тесты проходят
```bash
docker-compose exec backend pytest tests/ -v
# Ожидается: 100+ tests passed
```

### 5. E2E workflow (полный цикл)
1. **Регистрация участника:**
   ```bash
   POST /api/v1/auth/register
   {
     "email": "student@example.com",
     "password": "secure123",
     "full_name": "Иван Иванов",
     "school": "Школа №1"
   }
   # → 201 Created, JWT token
   ```

2. **Создание соревнования (Admin):**
   ```bash
   POST /api/v1/admin/competitions
   {
     "name": "Олимпиада по математике",
     "date": "2026-03-15",
     "variants_count": 4,
     "max_score": 100
   }
   # → 201 Created
   ```

3. **Регистрация на соревнование:**
   ```bash
   POST /api/v1/competitions/{id}/register
   # → 201 Created, registration_id
   ```

4. **Получить входной QR:**
   ```bash
   GET /api/v1/competitions/{id}/entry-qr
   # → 200 OK, {qr_code: "base64_image", token: "..."}
   ```

5. **Admitter сканирует QR:**
   ```bash
   POST /api/v1/admission/verify
   {
     "qr_code": "токен_из_qr"
   }
   # → 200 OK, {participant_name, competition_name, can_proceed: true}
   ```

6. **Подтвердить допуск и получить бланк:**
   ```bash
   POST /api/v1/admission/{id}/approve
   # → 201 Created, {pdf_url: "minio_url", attempt_id}
   ```

7. **Scanner загружает скан:**
   ```bash
   POST /api/v1/scans/upload
   Content-Type: multipart/form-data
   file: scan.pdf
   # → 202 Accepted, {scan_id, task_id}
   ```

8. **Celery обрабатывает скан (автоматически):**
   ```bash
   # Проверить статус задачи
   GET /api/v1/scans/{scan_id}
   # → 200 OK, {ocr_score: 85, confidence: 0.95, status: "completed"}
   ```

9. **Применить балл (если confidence низкий):**
   ```bash
   POST /api/v1/attempts/{attempt_id}/apply-score
   {
     "score": 85
   }
   # → 200 OK, attempt.status = SCORED
   ```

10. **Admin публикует результаты:**
    ```bash
    POST /api/v1/admin/competitions/{id}/publish
    # → 200 OK, competition.status = PUBLISHED
    ```

11. **Участник видит результаты:**
    ```bash
    GET /api/v1/results/{competition_id}
    # → 200 OK, [{full_name, score, rank}, ...]
    ```

### 6. Security checks
- ✅ Попытка использовать entry_token дважды → 400 "Token already used"
- ✅ Попытка доступа к admitter endpoint с participant ролью → 403 Forbidden
- ✅ JWT с истекшим сроком → 401 Unauthorized
- ✅ Некорректный QR токен → 404 "Token not found"
- ✅ SQL injection в параметрах → безопасно (SQLAlchemy prepared statements)

### 7. OCR accuracy test
Создать 100 тестовых бланков с разными баллами → сканировать → проверить accuracy:
```bash
pytest tests/e2e/test_ocr_accuracy.py
# Ожидается: accuracy ≥ 95%
```

### 8. Load testing
```bash
# 1000 одновременных регистраций
ab -n 1000 -c 100 -H "Authorization: Bearer {token}" \
   -p registration.json -T application/json \
   http://localhost:8000/api/v1/competitions/{id}/register

# Ожидается: avg response time < 500ms, 0 failures
```

### 9. Audit log проверка
```bash
# Проверить, что все действия залогированы
docker-compose exec postgres psql -U olimpqr_user -d olimpqr
SELECT entity_type, action, COUNT(*) FROM audit_log GROUP BY entity_type, action;
# Ожидается: записи для всех операций (registration, admission, score_applied, published)
```

### 10. Frontend интеграция
1. Открыть http://localhost (nginx)
2. Зарегистрироваться как участник
3. Записаться на соревнование
4. Отобразить entry QR
5. Открыть в новом окне как Admitter
6. Сканировать QR через камеру (html5-qrcode)
7. Подтвердить допуск → скачать PDF бланк
8. Открыть как Scanner
9. Загрузить скан → увидеть OCR результат
10. Открыть как Admin → опубликовать результаты
11. Публичная страница отображает результаты

---

## Потенциальные риски и митигация

### Риск 1: OCR низкая точность на рукописном тексте
**Митигация:**
- Использовать печатные цифры (Scanner пишет печатными буквами)
- Предобработка изображения (контраст, бинаризация)
- Ручная проверка при confidence < 0.7
- Обучить custom модель PaddleOCR на реальных данных (опционально)

### Риск 2: QR код не распознается со скана
**Митигация:**
- Использовать высокое качество QR (error_correction=H)
- Крупный размер QR на бланке (40x40mm)
- Библиотека pyzbar для извлечения QR из изображения
- Fallback: ручной ввод sheet_token

### Риск 3: Performance bottleneck при 1000+ участников
**Митигация:**
- Асинхронный FastAPI (uvicorn workers)
- Celery для OCR (несколько workers)
- PostgreSQL индексы на критичных полях
- MinIO для горизонтального масштабирования storage
- Redis caching для часто запрашиваемых данных

### Риск 4: Утечка токенов из БД
**Митигация:**
- Хранить только HMAC hash (нельзя восстановить исходный токен)
- HTTPS обязательно (токены не передаются в открытом виде)
- Rate limiting для предотвращения brute-force
- Audit log для отслеживания подозрительных действий

### Риск 5: Docker контейнеры не запускаются на production
**Митигация:**
- Тестировать docker-compose.prod.yml на staging
- Health checks для всех сервисов
- CI/CD pipeline с автоматическими проверками
- Rollback стратегия в GitLab CI

---

## Итоги

**Объем работы:** ~200-250 часов чистого coding (10 недель solo или 5 недель team of 2)

**Сложность:** Высокая (микросервисная архитектура, OCR, безопасность, 4 роли)

**Ключевые преимущества подхода:**
- ✅ Clean Architecture → легко тестировать и поддерживать
- ✅ HMAC токены → невозможно подделать QR без доступа к серверу
- ✅ Асинхронный OCR (Celery) → не блокирует API
- ✅ Docker → воспроизводимость окружения
- ✅ GitLab CI/CD → автоматизация тестов и деплоя
- ✅ TypeScript → type safety на frontend
- ✅ Audit log → полная прозрачность операций

**Критерии успеха:**
- Участник может пройти full cycle: регистрация → entry QR → допуск → бланк → скан → балл → публикация
- OCR распознает ≥95% баллов автоматически
- Система выдерживает 1000+ одновременных пользователей
- Невозможно подделать QR или определить участника без БД
- Все критичные действия залогированы
