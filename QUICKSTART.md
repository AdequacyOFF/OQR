# Quick Start Guide

## Запуск проекта за 5 минут

### 1. Запустите Docker контейнеры

```bash
cd D:\Projects\Kafedra\OlimpQR
docker-compose up -d
```

Это запустит:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- MinIO (порт 9000, консоль 9001)
- Backend FastAPI (порт 8000)
- Celery Worker
- Frontend Vite (порт 5173)

### 2. Проверьте статус сервисов

```bash
docker-compose ps
```

Все сервисы должны быть в статусе "Up".

### 3. Примените миграции БД

```bash
docker-compose exec backend alembic upgrade head
```

### 4. Откройте приложение

- **Swagger API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173
- **MinIO Console**: http://localhost:9001 (minioadmin / minioadmin)

### 5. Тестирование API

#### Регистрация участника

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "securepass123",
    "role": "participant",
    "full_name": "Иван Иванов",
    "school": "Школа №1",
    "grade": 10
  }'
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "...",
  "email": "student@example.com",
  "role": "participant"
}
```

#### Логин

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "securepass123"
  }'
```

#### Получить информацию о текущем пользователе

```bash
# Используйте access_token из предыдущего ответа
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 6. Остановка и очистка

```bash
# Остановить сервисы
docker-compose down

# Остановить и удалить volumes (БД, Redis, MinIO данные)
docker-compose down -v
```

## Разработка

### Backend

```bash
cd backend

# Установить зависимости
poetry install

# Запустить тесты
poetry run pytest

# Запустить линтер
poetry run ruff check src/
```

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Запустить dev server
npm run dev

# Запустить линтер
npm run lint
```

## Troubleshooting

### Backend не запускается

```bash
# Проверить логи
docker-compose logs backend

# Пересоздать контейнер
docker-compose up -d --force-recreate backend
```

### Ошибка подключения к БД

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Проверить логи
docker-compose logs postgres

# Подключиться к БД вручную
docker-compose exec postgres psql -U olimpqr_user -d olimpqr
```

### MinIO недоступен

```bash
# Проверить статус
docker-compose ps minio

# Перезапустить
docker-compose restart minio
```

## Следующие шаги

1. Ознакомьтесь с [README.md](README.md) для полной документации
2. Изучите API через Swagger UI: http://localhost:8000/docs
3. Начните разработку с создания competitions API
4. Реализуйте registration flow
5. Добавьте PDF generator для answer sheets
6. Настройте OCR для распознавания баллов

## Полезные команды

```bash
# Логи всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Войти в контейнер
docker-compose exec backend bash

# Применить новую миграцию
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head

# Запустить Python REPL в контейнере
docker-compose exec backend python

# Очистить все Docker ресурсы
docker system prune -a
```
