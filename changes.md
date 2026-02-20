You are Claude Code (opus-4-6), acting as a senior full-stack engineer.

Project: OlimpQR (FastAPI + async SQLAlchemy + Alembic + Celery + MinIO + React/TypeScript + Vite).
The current architecture and features are described in DOCUMENTATION.md (Clean Architecture, roles Participant/Admitter/Scanner/Admin, QR entry_token + sheet_token, PDF generation, OCR pipeline).

Goal: implement the new requirements below, update docs, add DB migrations, tests, and UI. Work iteratively:
(1) design/models/migrations, (2) use-cases + repositories + API, (3) frontend, (4) tests, (5) docs.

MANDATORY:
- Keep Clean Architecture boundaries: presentation → application → domain; infrastructure implements interfaces.
- All DB changes via Alembic migrations.
- Update RBAC and the access matrix.
- Add/update Pydantic schemas and frontend types.
- Add tests (unit/integration/e2e where appropriate).
- Update DOCUMENTATION.md: architecture, DB schema, flows, roles, endpoints, frontend routes.

Constraints / realism notes:
- A “laser” QR scanner typically works as USB HID (keyboard wedge): it “types” the scanned string into the focused input, often followed by Enter. Support this as the primary scenario in the UI. Optionally leave an extension point for COM/Serial mode, but do not hard-bind to a specific device.
- For document verification on the Admitter screen: use a browser PDF viewer (embed/iframe/pdfjs). If the upload is an image, display it.

========================================================
Requirements (as tasks)
========================================================

1) Admission module (Admitter): add QR reading via “laser”
- Currently admission: /admission (scan admission QR via camera/component).
- Add an alternative mode: external laser scanner that inputs the QR string into a field.
- UI: toggle “Camera / Laser”. In “Laser” mode the input is always focused; after the string/Enter, automatically call verify/approve.

2) “School” → “Educational institution” + institutions directory + rooms + seating/variant assignment + documents + DOB

2.1 Field replacement
- Replace participants.school with “educational institution”.
- Create an institutions directory: table institutions (id, name, short_name, city?, created_at...).
- During participant registration: “educational institution” is selected via search and/or dropdown (autocomplete).
- Admin panel: CRUD for institutions + search.

2.2 Competition rooms + seating + variants
- When creating/editing a competition, admin defines a list of rooms:
  - room: id, competition_id, name/number, capacity (optionally rows/cols or a seat_map).
- When scanning an admission QR (entry token), the system must:
  - shuffle/distribute participants from the SAME institution across different rooms and seats,
  - assign a seat and a room,
  - assign a problem variant (competitions already have variants_count),
  - return these fields to the Admitter screen immediately after scan/approval.
- Requirement: assignment must be stable (must not change on repeated calls). Once room/seat/variant is assigned it must be stored in DB.
- Propose a simple safe algorithm:
  - on approve, create/update the participant’s attempt and seat assignment for the registration,
  - for shuffling use a deterministic seed (competition_id + institution_id) OR transactional random selection of free seats with persistence,
  - avoid race conditions: transactions + unique constraints (e.g., unique(room_id, seat_number)).

2.3 Documents + date of birth
- Add to participant registration:
  - date of birth (dob)
  - upload of identity document scans (passport or military ID).
- Store files in MinIO (new bucket or reuse scans; prefer a dedicated bucket like documents).
- On Admitter side: when verifying admission, show the uploaded document in a PDF viewer (or an image viewer) plus participant data for visual comparison.

3) Separate Invigilator module: scan participant sheet QR for exits/entries + timings + unlimited extra answer sheets

3.1 Role and module
- Add a new role: invigilator. Update UserRole enum, RBAC, frontend routes, access matrix.
- New screen /invigilator: support scanning participant sheet QR:
  - via camera and/or laser (same as admission).
- Each scan can be used to record events:
  - start_work_time — the first time the participant starts working (trigger via QR + action button, or auto on first scan),
  - submit_time — via QR + action,
  - exit_time — leaving the room,
  - enter_time — entering back.
- In Invigilator module display timing metrics for the current participant: last activity, total time out, list of exit/enter events.

3.2 Extra answer sheets
- Invigilator must be able to issue an “extra answer sheet” infinitely:
  - create an extra sheet entity linked to the primary attempt/registration.
  - IMPORTANT: the final score must remain computed ONLY from the primary (original) sheet. Extra sheets store answers but do not affect score_total.
- Scanner module: add support for scanning/uploading multiple sheets for a single participant:
  - when reading a sheet QR, determine whether it’s primary or extra,
  - group in UI as “Attempt + N extra sheets”.
- Design the data model carefully:
  - Option A (preferred): answer_sheets table (id, attempt_id, sheet_token_hash, kind=primary|extra, created_at)
    and scans reference answer_sheet_id instead of attempt_id
  - Option B: model extras as attempts with parent_attempt_id (riskier for score/status logic)
  - Choose the cleaner option and update the OCR pipeline linking by sheet_token_hash.

4) Update DOCUMENTATION.md
- Add descriptions of:
  - new role (invigilator),
  - new tables: institutions, rooms, seat_assignments, documents, (answer_sheets + events),
  - new/changed endpoints,
  - updated flows for admission/invigilator/scanner,
  - updated frontend routing,
  - QR structure changes (if any) for extra sheets.

5) Summarize tasks + create an MD plan file with completion checkboxes
- Create a new file PLAN.md (or TASKS.md) at the repo root / next to documentation:
  - checklist for tasks 1–4,
  - status [ ] / [x],
  - short “definition of done” for each.
- As you implement, mark items as [x] within the branch/PR.

========================================================
What I need from you (deliverables)
========================================================
Implement the changes in the codebase:
- Backend: domain/use-cases/repositories/endpoints, Alembic migrations, MinIO storage for documents, audit logging where appropriate.
- Frontend: new forms/fields, institution autocomplete, admin CRUD for institutions and rooms, scanning modes, PDF viewer, separate Invigilator module, update types and API client.
- Tests: at minimum new unit/integration tests for the assignment algorithm and event tracking; e2e for key flows (register → admit → assign room/seat/variant → invigilator exit/enter → scanner multi-sheet).
- Documentation: update DOCUMENTATION.md + add PLAN.md checklist.

Strict working order:
1) Propose a detailed data schema (ERD in text) and a list of required migrations.
2) List new/changed REST endpoints and role-based access.
3) Implement step-by-step with small logical commits.
4) Finish by updating docs and PLAN.md, and output a final summary of what was done + how to verify (test commands).
Start by analyzing existing models and routes (/api/v1/admission, /api/v1/scans, /api/v1/admin, registration) and propose the least-breaking extension approach.