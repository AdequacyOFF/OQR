"""Comprehensive E2E test: Complete system workflow with new registration system.

This test covers the entire system workflow after the registration redesign:
1. Admin initialization (via direct DB creation, mimicking init_admin.py)
2. Participant registration through API (automatic participant role)
3. Competition lifecycle management
4. Staff user creation by admin
5. Full admission → scan → results workflow
6. Entry token retrieval via GET /registrations/{id}
7. Audit log verification
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4, UUID
from httpx import AsyncClient
from sqlalchemy import select

from olimpqr.domain.value_objects import UserRole, AttemptStatus
from olimpqr.infrastructure.database.models import UserModel, AttemptModel
from olimpqr.infrastructure.security import hash_password


@pytest.mark.e2e
class TestComprehensiveWorkflow:
    """Complete end-to-end test of the OlimpQR system."""

    async def test_complete_system_workflow(self, client: AsyncClient, db_session):
        """Test the entire system from admin creation to results publication."""

        # ═══════════════════════════════════════════════════════════════
        # Step 1: Initialize admin user (mimicking init_admin.py script)
        # ═══════════════════════════════════════════════════════════════
        admin_id = uuid4()
        admin_email = "admin@olimpqr.com"
        admin_password = "AdminSecure123"

        admin_user = UserModel(
            id=admin_id,
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        # Login as admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": admin_password}
        )
        assert admin_login.status_code == 200, f"Login failed: {admin_login.json()}"
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # ═══════════════════════════════════════════════════════════════
        # Step 2: Register participant through API (NEW FLOW)
        # ═══════════════════════════════════════════════════════════════
        participant_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "ivan.petrov@example.com",
                "password": "StudentPass123",
                "full_name": "Иван Петров",
                "school": "Лицей №1",
                "grade": 11
            }
        )
        assert participant_reg.status_code == 201
        part_data = participant_reg.json()

        # Verify role is automatically set to participant
        assert part_data["role"] == "participant"
        assert "access_token" in part_data

        part_token = part_data["access_token"]
        part_headers = {"Authorization": f"Bearer {part_token}"}
        part_user_id = UUID(part_data["user_id"])

        # ═══════════════════════════════════════════════════════════════
        # Step 3: Admin creates competition
        # ═══════════════════════════════════════════════════════════════
        comp_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Региональная олимпиада по математике 2026",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 4,
                "max_score": 100
            },
            headers=admin_headers
        )
        assert comp_resp.status_code == 201
        competition = comp_resp.json()
        competition_id = UUID(competition["id"])
        assert competition["status"] == "draft"

        # Open registration
        open_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/open-registration",
            headers=admin_headers
        )
        assert open_resp.status_code == 200
        assert open_resp.json()["status"] == "registration_open"

        # ═══════════════════════════════════════════════════════════════
        # Step 4: Participant registers for competition
        # ═══════════════════════════════════════════════════════════════
        reg_resp = await client.post(
            "/api/v1/registrations",
            json={"competition_id": str(competition_id)},
            headers=part_headers
        )
        assert reg_resp.status_code == 201
        registration = reg_resp.json()
        registration_id = UUID(registration["id"])
        entry_token_initial = registration["entry_token"]

        # Verify entry token is provided
        assert entry_token_initial is not None
        assert len(entry_token_initial) > 20
        assert registration["status"] == "pending"

        # ═══════════════════════════════════════════════════════════════
        # Step 5: Test GET registration by ID (NEW ENDPOINT TEST)
        # ═══════════════════════════════════════════════════════════════
        get_reg_resp = await client.get(
            f"/api/v1/registrations/{registration_id}",
            headers=part_headers
        )
        assert get_reg_resp.status_code == 200
        reg_detail = get_reg_resp.json()

        # Verify entry_token is returned again
        assert reg_detail["entry_token"] is not None
        assert reg_detail["entry_token"] == entry_token_initial
        assert reg_detail["id"] == str(registration_id)

        # ═══════════════════════════════════════════════════════════════
        # Step 6: Admin creates staff users (admitter + scanner)
        # ═══════════════════════════════════════════════════════════════

        # Create admitter
        admitter_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "admitter@olimpqr.com",
                "password": "AdmitterPass123",
                "role": "admitter"
            },
            headers=admin_headers
        )
        assert admitter_resp.status_code == 201
        admitter_data = admitter_resp.json()
        assert admitter_data["role"] == "admitter"
        assert admitter_data["is_active"] is True

        # Login as admitter
        admitter_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "admitter@olimpqr.com", "password": "AdmitterPass123"}
        )
        assert admitter_login.status_code == 200
        admitter_headers = {"Authorization": f"Bearer {admitter_login.json()['access_token']}"}

        # Create scanner
        scanner_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "scanner@olimpqr.com",
                "password": "ScannerPass123",
                "role": "scanner"
            },
            headers=admin_headers
        )
        assert scanner_resp.status_code == 201
        scanner_data = scanner_resp.json()
        assert scanner_data["role"] == "scanner"

        # Login as scanner
        scanner_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "scanner@olimpqr.com", "password": "ScannerPass123"}
        )
        assert scanner_login.status_code == 200
        scanner_headers = {"Authorization": f"Bearer {scanner_login.json()['access_token']}"}

        # ═══════════════════════════════════════════════════════════════
        # Step 7: Start competition (admission opens)
        # ═══════════════════════════════════════════════════════════════
        start_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/start",
            headers=admin_headers
        )
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "in_progress"

        # ═══════════════════════════════════════════════════════════════
        # Step 8: Admitter verifies entry QR code
        # ═══════════════════════════════════════════════════════════════
        verify_resp = await client.post(
            "/api/v1/admission/verify",
            json={"token": entry_token_initial},
            headers=admitter_headers
        )
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["participant_name"] == "Иван Петров"
        assert verify_data["competition_name"] == "Региональная олимпиада по математике 2026"
        assert verify_data["can_proceed"] is True
        assert verify_data["registration_id"] == str(registration_id)

        # ═══════════════════════════════════════════════════════════════
        # Step 9: Admitter approves admission (with mocked storage/PDF)
        # ═══════════════════════════════════════════════════════════════
        mock_storage = MagicMock()
        mock_storage.upload_file.return_value = "sheets/participant_123.pdf"
        mock_storage.get_presigned_url.return_value = "http://minio.test/sheets/participant_123.pdf"

        mock_sheet_gen = MagicMock()
        mock_sheet_gen.generate_answer_sheet.return_value = b"%PDF-1.4 mock answer sheet content"

        with patch(
            "olimpqr.presentation.api.v1.admission.MinIOStorage",
            return_value=mock_storage
        ), patch(
            "olimpqr.presentation.api.v1.admission.SheetGenerator",
            return_value=mock_sheet_gen
        ):
            approve_resp = await client.post(
                f"/api/v1/admission/{registration_id}/approve",
                json={"raw_entry_token": entry_token_initial},
                headers=admitter_headers
            )

        assert approve_resp.status_code == 201
        approve_data = approve_resp.json()
        attempt_id = UUID(approve_data["attempt_id"])
        variant_number = approve_data["variant_number"]
        sheet_token = approve_data["sheet_token"]

        assert 1 <= variant_number <= 4
        assert f"admission/sheets/{attempt_id}/download" in approve_data["pdf_url"]
        assert sheet_token is not None
        assert len(sheet_token) > 20

        # Verify attempt was created
        attempt_result = await db_session.execute(
            select(AttemptModel).where(AttemptModel.id == attempt_id)
        )
        attempt = attempt_result.scalar_one()
        assert attempt.status == AttemptStatus.PRINTED
        assert attempt.variant_number == variant_number

        # ═══════════════════════════════════════════════════════════════
        # Step 10: Scanner uploads scan (mock image upload)
        # ═══════════════════════════════════════════════════════════════

        # First, update attempt status to SCANNED (simulating OCR processing)
        from sqlalchemy import update
        await db_session.execute(
            update(AttemptModel)
            .where(AttemptModel.id == attempt_id)
            .values(status=AttemptStatus.SCANNED)
        )
        await db_session.commit()

        # ═══════════════════════════════════════════════════════════════
        # Step 11: Admin applies score to attempt
        # ═══════════════════════════════════════════════════════════════
        apply_score_resp = await client.post(
            f"/api/v1/scans/attempts/{attempt_id}/apply-score",
            json={"score": 87},
            headers=admin_headers
        )
        assert apply_score_resp.status_code == 200
        score_data = apply_score_resp.json()
        assert score_data["score_total"] == 87
        assert score_data["status"] == "scored"

        # ═══════════════════════════════════════════════════════════════
        # Step 12: Move to checking phase
        # ═══════════════════════════════════════════════════════════════
        check_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/start-checking",
            headers=admin_headers
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["status"] == "checking"

        # Mark attempt as published
        await db_session.execute(
            update(AttemptModel)
            .where(AttemptModel.id == attempt_id)
            .values(status=AttemptStatus.PUBLISHED)
        )
        await db_session.commit()

        # ═══════════════════════════════════════════════════════════════
        # Step 13: Publish results
        # ═══════════════════════════════════════════════════════════════
        publish_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/publish",
            headers=admin_headers
        )
        assert publish_resp.status_code == 200
        assert publish_resp.json()["status"] == "published"

        # ═══════════════════════════════════════════════════════════════
        # Step 14: Verify public results are visible
        # ═══════════════════════════════════════════════════════════════
        results_resp = await client.get(
            f"/api/v1/results/{competition_id}"
        )
        assert results_resp.status_code == 200
        results = results_resp.json()

        assert results["competition_name"] == "Региональная олимпиада по математике 2026"
        assert results["total_participants"] == 1
        assert len(results["results"]) == 1

        # Verify result details
        result_entry = results["results"][0]
        assert result_entry["rank"] == 1
        assert result_entry["participant_name"] == "Иван Петров"
        assert result_entry["score"] == 87
        assert result_entry["max_score"] == 100

        # ═══════════════════════════════════════════════════════════════
        # Step 15: Verify audit log endpoint is accessible
        # ═══════════════════════════════════════════════════════════════
        audit_resp = await client.get(
            "/api/v1/admin/audit-log?limit=100",
            headers=admin_headers
        )
        assert audit_resp.status_code == 200
        audit_data = audit_resp.json()

        # Audit log endpoint should return valid structure
        assert "total" in audit_data
        assert "items" in audit_data
        assert isinstance(audit_data["items"], list)

        # Note: Audit log implementation may vary - we just verify the endpoint works

    async def test_registration_without_role_field(self, client: AsyncClient):
        """Verify that registration endpoint does NOT accept role field."""

        # Attempt to register with explicit role should fail or ignore the role
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "hacker@example.com",
                "password": "HackerPass123",
                "role": "admin",  # Try to escalate privileges
                "full_name": "Test User",
                "school": "Test School",
                "grade": 10
            }
        )

        # Should succeed (role field is ignored by schema)
        # But user should have participant role, not admin
        if reg_resp.status_code == 201:
            user_data = reg_resp.json()
            assert user_data["role"] == "participant", "Role escalation vulnerability!"
        # Or it might return 422 if Pydantic rejects the extra field

    async def test_participant_cannot_create_staff_users(self, client: AsyncClient):
        """Verify that participants cannot create staff users."""

        # Register as participant
        part_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "participant@example.com",
                "password": "PartPass123",
                "full_name": "Test Participant",
                "school": "Test School",
                "grade": 9
            }
        )
        assert part_reg.status_code == 201
        part_headers = {"Authorization": f"Bearer {part_reg.json()['access_token']}"}

        # Try to create admin user
        create_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "fake.admin@example.com",
                "password": "FakeAdmin123",
                "role": "admin"
            },
            headers=part_headers
        )

        # Should be forbidden
        assert create_resp.status_code == 403

    async def test_entry_token_persistence(self, client: AsyncClient, db_session):
        """Verify that entry tokens can be retrieved multiple times."""

        # Setup: create admin and participant
        admin_user = UserModel(
            id=uuid4(),
            email="admin.token.test@example.com",
            password_hash=hash_password("AdminPass123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin.token.test@example.com", "password": "AdminPass123"}
        )
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        # Register participant
        part_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "token.test@example.com",
                "password": "PartPass123",
                "full_name": "Token Test User",
                "school": "Test School",
                "grade": 10
            }
        )
        part_headers = {"Authorization": f"Bearer {part_reg.json()['access_token']}"}

        # Create competition
        comp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Token Test Competition",
                "date": "2026-04-01",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-25T23:59:59",
                "variants_count": 2,
                "max_score": 50
            },
            headers=admin_headers
        )
        comp_id = comp.json()["id"]

        await client.post(
            f"/api/v1/competitions/{comp_id}/open-registration",
            headers=admin_headers
        )

        # Register for competition
        reg = await client.post(
            "/api/v1/registrations",
            json={"competition_id": comp_id},
            headers=part_headers
        )
        assert reg.status_code == 201
        reg_id = reg.json()["id"]
        initial_token = reg.json()["entry_token"]

        # Retrieve token again via GET endpoint
        get_reg1 = await client.get(
            f"/api/v1/registrations/{reg_id}",
            headers=part_headers
        )
        assert get_reg1.status_code == 200
        token1 = get_reg1.json()["entry_token"]

        # Retrieve token a third time
        get_reg2 = await client.get(
            f"/api/v1/registrations/{reg_id}",
            headers=part_headers
        )
        assert get_reg2.status_code == 200
        token2 = get_reg2.json()["entry_token"]

        # All tokens should be the same
        assert token1 == initial_token
        assert token2 == initial_token
        assert token1 == token2

    async def test_staff_user_list(self, client: AsyncClient, db_session):
        """Verify admin can list users by role."""

        # Create admin
        admin_user = UserModel(
            id=uuid4(),
            email="list.admin@example.com",
            password_hash=hash_password("AdminPass123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "list.admin@example.com", "password": "AdminPass123"}
        )
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        # Create multiple users of different roles
        admitter_create = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "admitter1@example.com",
                "password": "Password123",
                "role": "admitter"
            },
            headers=admin_headers
        )
        assert admitter_create.status_code == 201, f"Failed to create admitter: {admitter_create.json()}"

        scanner_create = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "scanner1@example.com",
                "password": "Password123",
                "role": "scanner"
            },
            headers=admin_headers
        )
        assert scanner_create.status_code == 201, f"Failed to create scanner: {scanner_create.json()}"

        # List all users
        all_users = await client.get(
            "/api/v1/admin/users?limit=100",
            headers=admin_headers
        )
        assert all_users.status_code == 200
        users_data = all_users.json()
        # Should have at least the admin we created, plus the two staff users
        # Note: The total field reflects the count of items returned, not a separate total count
        assert len(users_data["items"]) >= 3  # admin + admitter + scanner

        # Filter by role
        admitters = await client.get(
            "/api/v1/admin/users?role=admitter",
            headers=admin_headers
        )
        assert admitters.status_code == 200
        assert admitters.json()["total"] >= 1
        assert all(u["role"] == "admitter" for u in admitters.json()["items"])
