# OlimpQR - Olympic Competition Management System

Веб-приложение для контроля проведения олимпиад с анонимными QR-кодами.

## Возможности

- **Регистрация участников** с выдачей входных QR-кодов
- **Допуск через сканирование QR** (одноразовое использование)
- **Генерация анонимных бланков** с уникальными QR-кодами
- **OCR распознавание** итоговых баллов из сканов (PaddleOCR)
- **Публикация результатов** для участников

## Безопасность

- QR-коды содержат криптографически стойкие токены (256 бит энтропии)
- В БД хранятся только HMAC-SHA256 хэши токенов
- По QR невозможно определить участника без доступа к серверу
- Все изменения статусов логируются в audit_log

## Технологический стек

### Backend
- Python 3.13 + Poetry
- FastAPI (async web framework)
- PostgreSQL 16 (БД)
- SQLAlchemy 2.0 (async ORM)
- Celery + Redis (очередь задач для OCR)
- MinIO (S3-compatible хранилище файлов)
- PaddleOCR + OpenCV (распознавание текста)
- ReportLab (генерация PDF бланков)

### Frontend
- React 18 + TypeScript
- Vite (сборщик)
- React Router 6 (навигация)
- Zustand (state management)
- Axios (HTTP клиент)
- html5-qrcode (сканирование QR)
- qrcode.react (отображение QR)

### Infrastructure
- Docker + docker-compose
- PostgreSQL, Redis, MinIO containers
- nginx (frontend static server)

## Быстрый старт

### Предварительные требования

- Docker Desktop (Windows) или Docker + docker-compose (Linux)
- Git
- 4GB+ RAM

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd OlimpQR
```

### 2. Настройка переменных окружения

```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env и установить SECRET_KEY и HMAC_SECRET_KEY
# Можно сгенерировать с помощью:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Важные переменные:**
- `SECRET_KEY` - для JWT токенов (минимум 32 символа)
- `HMAC_SECRET_KEY` - для HMAC хэширования QR токенов (минимум 32 символа)
- `POSTGRES_PASSWORD` - пароль PostgreSQL
- `MINIO_ACCESS_KEY` и `MINIO_SECRET_KEY` - доступ к MinIO

### 3. Запуск с помощью Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f backend
```

### 4. Применение миграций БД

```bash
# Применить миграции
docker-compose exec backend alembic upgrade head

# Проверить таблицы
docker-compose exec postgres psql -U olimpqr_user -d olimpqr -c "\dt"
```

### 5. Открыть приложение

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)

## Разработка

### Backend

```bash
# Установить зависимости
cd backend
poetry install

# Запустить сервер локально (требуется running БД)
poetry run uvicorn olimpqr.main:app --reload

# Запустить тесты
poetry run pytest

# Линтинг
poetry run ruff check src/
poetry run mypy src/
```

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev server
npm run dev

# Сборка для production
npm run build

# Линтинг
npm run lint
```

## Архитектура

### Backend: Clean Architecture

```
backend/src/olimpqr/
├── domain/              # Бизнес-логика
│   ├── entities/        # User, Competition, Attempt, Scan
│   ├── value_objects/   # Token, Score, UserRole
│   ├── services/        # TokenService, QRService
│   └── repositories/    # Интерфейсы репозиториев
├── application/         # Use Cases
│   ├── use_cases/       # RegisterUser, VerifyQR, ProcessOCR
│   ├── dto/             # Data Transfer Objects
│   └── interfaces/      # OCRService, PDFService, StorageService
├── infrastructure/      # Технические реализации
│   ├── database/        # SQLAlchemy модели + репозитории
│   ├── ocr/             # PaddleOCR + OpenCV
│   ├── pdf/             # ReportLab генератор бланков
│   ├── storage/         # MinIO клиент
│   ├── tasks/           # Celery tasks
│   └── security/        # JWT, password hashing
└── presentation/        # API Layer
    ├── api/v1/          # FastAPI endpoints
    ├── dependencies/    # Auth, DB session
    └── schemas/         # Pydantic модели
```

### Роли пользователей

1. **Participant** - Участник олимпиады
   - Регистрация на соревнования
   - Просмотр входного QR кода
   - Просмотр результатов

2. **Admitter** - Принимающий на вход
   - Сканирование входных QR кодов
   - Подтверждение допуска
   - Генерация и печать бланков

3. **Scanner** - Проверяющий работы
   - Загрузка сканов работ
   - Проверка OCR результатов
   - Ручная корректировка баллов

4. **Admin** - Администратор
   - Управление соревнованиями (CRUD)
   - Управление пользователями
   - Публикация результатов
   - Просмотр audit log

## Основные workflow

### 1. Регистрация и допуск участника

```
Participant → Регистрация на олимпиаду
           → Получение entry QR кода

Admitter   → Сканирование entry QR
           → Подтверждение допуска
           → Генерация бланка с sheet QR
           → Печать и выдача бланка
```

### 2. Проверка работы

```
Scanner → Загрузка скана работы
        → Celery: OCR обработка (автоматически)
        → Если confidence >= 0.7 → балл применяется автоматически
        → Если confidence < 0.7 → требуется ручная проверка
        → Scanner проверяет и корректирует при необходимости
```

### 3. Публикация результатов

```
Admin → Проверка всех результатов
      → Публикация соревнования
      → Результаты становятся видны участникам
```

## API Endpoints

### Auth
- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/login` - Вход (получение JWT)

### Competitions
- `GET /api/v1/competitions` - Список соревнований
- `POST /api/v1/competitions` - Создать соревнование (admin)
- `POST /api/v1/competitions/{id}/register` - Зарегистрироваться (participant)

### Admission (Admitter)
- `POST /api/v1/admission/verify` - Проверить entry QR
- `POST /api/v1/admission/{id}/approve` - Подтвердить допуск и создать бланк

### Scans (Scanner)
- `POST /api/v1/scans/upload` - Загрузить скан
- `GET /api/v1/scans` - Список сканов
- `POST /api/v1/scans/{id}/verify` - Подтвердить/исправить OCR результат

### Results (Public)
- `GET /api/v1/results/{competition_id}` - Результаты соревнования

## Тестирование

```bash
cd backend

# Все тесты (124 теста)
poetry run pytest

# Unit tests (54 теста)
poetry run pytest tests/unit -v

# Integration tests (40 тестов)
poetry run pytest tests/integration -v

# E2E tests (30 тестов — полный workflow + OCR pipeline)
poetry run pytest tests/e2e -v

# С покрытием
poetry run pytest --cov=olimpqr --cov-report=html
```

### Frontend

```bash
cd frontend

# Проверка TypeScript
npx tsc --noEmit

# Линтинг
npm run lint
```

## Production Deployment

### Подготовка

1. Обновить `.env` с production значениями:
   - Установить `ENVIRONMENT=production`
   - Установить `DEBUG=false`
   - Сгенерировать надежные SECRET_KEY и HMAC_SECRET_KEY
   - Установить production пароли для БД

2. Обновить `BACKEND_CORS_ORIGINS` с production доменами

### Docker Compose Production

```bash
# Использовать production конфигурацию
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Применить миграции
docker-compose exec backend alembic upgrade head
```

### Мониторинг

```bash
# Логи
docker-compose logs -f backend
docker-compose logs -f celery-worker

# Здоровье сервисов
docker-compose ps
curl http://localhost:8000/health

# Метрики PostgreSQL
docker-compose exec postgres psql -U olimpqr_user -d olimpqr -c "SELECT * FROM pg_stat_activity;"
```

## Безопасность

### Критические компоненты

1. **TokenService** - генерация и проверка токенов
   - 256 бит энтропии (secrets.token_urlsafe(32))
   - HMAC-SHA256 хэширование
   - Constant-time comparison (hmac.compare_digest)

2. **Хранение токенов**
   - В БД: только HMAC hash
   - В QR: raw token
   - Raw token никогда не сохраняется

3. **Одноразовое использование**
   - entry_token.used_at проверяется перед допуском
   - После использования невозможно повторно войти

4. **Rate Limiting** (slowapi)
   - Registration: 3 запроса/мин на IP
   - Login: 5 запросов/мин на IP
   - Общий лимит: 100 запросов/мин

5. **Audit Log**
   - Все критические действия логируются
   - entity_type, entity_id, action, user_id, IP, timestamp
   - JSON details для дополнительного контекста

### Security Checklist

- [x] SECRET_KEY и HMAC_SECRET_KEY >= 32 символов
- [ ] HTTPS enabled (production)
- [x] CORS configured с правильными origins
- [x] Rate limiting active (slowapi)
- [x] SQL injection prevention (SQLAlchemy параметризованные запросы)
- [x] XSS prevention (React auto-escaping)
- [x] JWT с разумным expire time
- [x] Пароли хэшированы с bcrypt

## Troubleshooting

### Проблема: Backend не запускается

```bash
# Проверить логи
docker-compose logs backend

# Проверить подключение к БД
docker-compose exec postgres psql -U olimpqr_user -d olimpqr -c "SELECT 1;"

# Пересоздать контейнер
docker-compose up -d --force-recreate backend
```

### Проблема: OCR не распознает баллы

1. Проверить качество скана (минимум 300 DPI)
2. Убедиться, что область балла фиксирована на бланке
3. Проверить координаты в config: OCR_SCORE_FIELD_X, OCR_SCORE_FIELD_Y
4. Включить DEBUG для PaddleOCR логов

### Проблема: MinIO недоступен

```bash
# Проверить статус
docker-compose ps minio

# Проверить доступ
curl http://localhost:9000/minio/health/live

# Пересоздать buckets
docker-compose exec backend python -c "from olimpqr.infrastructure.storage import init_buckets; init_buckets()"
```

## Лицензия

MIT

## Контакты

- Email: andrey_stolov@mail.ru
- GitHub: StolovAR
