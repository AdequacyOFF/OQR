# OlimpQR - План задач

## Задача 1: Лазерный QR-сканер в модуле допуска

- [x] Добавить режим "Лазер" на страницу допуска (`AdmissionPage.tsx`)
- [x] Реализовать переключатель "Камера / Загрузка / Лазер"
- [x] В режиме "Лазер": авто-фокусируемый `<input>`, по Enter — автоматический вызов verify → approve
- [x] USB HID сканер вводит строку QR + Enter как клавиатурное устройство

**Критерий выполнения:** На странице `/admission` есть переключатель "Лазер", при считывании QR лазером строка автоматически обрабатывается.

---

## Задача 2: Учебные учреждения + аудитории + рассадка + варианты + документы + дата рождения

### 2.1 Справочник учебных учреждений
- [x] Создать таблицу `institutions` (id, name, short_name, city, created_at)
- [x] Alembic миграция 004: создание таблицы + перенос данных из `participants.school`
- [x] Доменная сущность `Institution` с валидацией
- [x] Репозиторий `InstitutionRepository` (search, get_by_name, CRUD)
- [x] Use Cases: `CreateInstitution`, `ListInstitutions`, `SearchInstitutions`
- [x] API-эндпоинты: GET /institutions (публичный), POST/DELETE (admin)
- [x] Фронтенд: компонент `InstitutionAutocomplete` с поиском
- [x] Фронтенд: страница `InstitutionsPage` (CRUD, админ)
- [x] Добавить `institution_id` FK в таблицу `participants`

### 2.2 Аудитории и рассадка
- [x] Создать таблицу `rooms` (id, competition_id, name, capacity) с уникальным constraint (competition_id, name)
- [x] Создать таблицу `seat_assignments` (registration_id unique, room_id, seat_number, variant_number) с уникальным constraint (room_id, seat_number)
- [x] Alembic миграция 005: rooms + seat_assignments
- [x] Доменные сущности: `Room`, `SeatAssignment`
- [x] Репозитории: `RoomRepository`, `SeatAssignmentRepository`
- [x] Use Cases: `CreateRoom`, `ListRooms`, `DeleteRoom`
- [x] **Алгоритм рассадки** (`AssignSeatUseCase`):
  - Выбор аудитории с наименьшим количеством участников из того же учреждения
  - Tie-break: наибольшее количество свободных мест
  - Назначение следующего свободного места
  - Назначение варианта: `(seat_number % variants_count) + 1`
  - Идемпотентность: повторный вызов возвращает существующую рассадку
- [x] API-эндпоинты: GET/POST/DELETE /rooms/{competition_id} (admin)
- [x] Фронтенд: страница `RoomsPage` (управление аудиториями)
- [x] Интеграция в approve_admission: после допуска показать аудиторию + место + вариант

### 2.3 Документы и дата рождения
- [x] Добавить `dob` (дата рождения) в таблицу `participants`
- [x] Создать таблицу `documents` (id, participant_id, file_path, file_type, created_at)
- [x] Alembic миграция 006: documents
- [x] Доменная сущность `Document`
- [x] Репозиторий `DocumentRepository`
- [x] Use Cases: `UploadDocument`, `GetParticipantDocuments`
- [x] API-эндпоинты: POST /documents (participant), GET /documents/participant/{id} (admin/admitter/invigilator)
- [x] При верификации допуска показать: учебное учреждение, дату рождения, наличие документов

**Критерий выполнения:** При допуске участника система автоматически назначает аудиторию, место и вариант с распределением участников одного учреждения по разным аудиториям.

---

## Задача 3: Модуль надзирателя (Invigilator)

### 3.1 Роль и модуль
- [x] Добавить роль `invigilator` в enum `UserRole`
- [x] Обновить `is_staff` property для включения надзирателя
- [x] Alembic миграция 007: ALTER TYPE userrole ADD VALUE 'invigilator'
- [x] Создать enum `EventType`: start_work, submit, exit_room, enter_room
- [x] Создать таблицу `participant_events` (id, attempt_id, event_type, timestamp, recorded_by)
- [x] Доменная сущность `ParticipantEvent`
- [x] Репозиторий `ParticipantEventRepository`
- [x] Use Cases: `RecordEvent`, `GetAttemptEvents`
- [x] API-эндпоинты: POST /invigilator/events, GET /invigilator/attempt/{id}/events
- [x] Фронтенд: страница `/invigilator` со сканером QR (камера + лазер), кнопками событий, историей

### 3.2 Дополнительные бланки ответов
- [x] Создать enum `SheetKind`: primary, extra
- [x] Создать таблицу `answer_sheets` (id, attempt_id, sheet_token_hash, kind, pdf_file_path, created_at)
- [x] Добавить `answer_sheet_id` FK в таблицу `scans`
- [x] Alembic миграция 007: answer_sheets + scans.answer_sheet_id + миграция данных из attempts
- [x] Доменная сущность `AnswerSheet`
- [x] Репозиторий `AnswerSheetRepository`
- [x] Use Case: `IssueExtraSheet` — создание доп. бланка по QR основного
- [x] API-эндпоинт: POST /invigilator/extra-sheet
- [x] При допуске (approve) автоматически создаётся `AnswerSheet(kind=primary)`
- [x] Фронтенд: кнопка выдачи доп. бланка, отображение QR нового бланка

**Критерий выполнения:** Надзиратель может сканировать QR бланка, фиксировать события (выход/вход/начало/сдача) и выдавать дополнительные бланки.

---

## Задача 4: Обновление документации

- [x] Обновить `DOCUMENTATION.md`:
  - [x] Новая роль (invigilator) в перечислениях и матрице доступа
  - [x] Новые таблицы: institutions, rooms, seat_assignments, documents, participant_events, answer_sheets
  - [x] Новые перечисления: EventType, SheetKind
  - [x] Новые/изменённые API-эндпоинты
  - [x] Обновлённые потоки: допуск с рассадкой, надзиратель, сканер с доп. бланками
  - [x] Обновлённые маршруты фронтенда
- [x] Создать `PLAN.md` с чеклистом задач

**Критерий выполнения:** Документация полностью отражает текущее состояние системы со всеми новыми функциями.

---

## Задача 5: Тестирование

- [x] Unit-тесты новых сущностей и value objects (25 тестов)
- [x] Unit-тесты алгоритма рассадки (4 теста)
- [x] Интеграционные тесты API учебных учреждений (6 тестов)
- [x] Интеграционные тесты API аудиторий (3 теста)
- [x] Интеграционные тесты API надзирателя (4 теста)
- [x] Обновлённые фикстуры: `invigilator_user`, `institution`
- [x] Обновлённые E2E тесты для нового формата ответа допуска

**Критерий выполнения:** Все 42 новых теста проходят. Существующие тесты не сломаны (9 pre-existing failures не связаны с нашими изменениями).

---

## Верификация

```bash
# Бэкенд: все тесты
cd backend && poetry run python -m pytest --no-cov

# Линтер
poetry run ruff check src/

# Типы
poetry run mypy src/

# Фронтенд: TypeScript
cd frontend && npx tsc --noEmit

# Фронтенд: сборка
npm run build
```
