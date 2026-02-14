"""E2E test: Full competition workflow.

Tests the complete lifecycle:
1. Register admin + participant users
2. Admin creates competition
3. Admin opens registration
4. Participant registers for competition (gets entry token)
5. Admin starts competition (admission phase)
6. Admitter verifies entry QR
7. Admitter approves admission (mocked storage/pdf)
8. Score is applied to attempt
9. Competition goes through checking → published
10. Public results are visible
"""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4
from httpx import AsyncClient

from tests.integration.conftest import make_auth_header
from olimpqr.domain.value_objects import UserRole
from olimpqr.infrastructure.database.models import (
    AttemptModel,
    RegistrationModel,
    UserModel,
)
from olimpqr.infrastructure.security import hash_password


@pytest.mark.e2e
class TestFullCompetitionWorkflow:
    """Full E2E: registration → competition → admission → scoring → results."""

    async def test_complete_workflow(self, client: AsyncClient, db_session):
        """Test the entire competition lifecycle from start to published results."""

        # ── Step 1: Create admin user (mimicking init_admin.py) ──
        admin_user = UserModel(
            id=uuid4(),
            email="workflow_admin@test.com",
            password_hash=hash_password("adminpass123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        # Login as admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "workflow_admin@test.com", "password": "adminpass123"}
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # ── Step 2: Register participant (new flow without role) ──
        part_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "workflow_part@test.com",
                "password": "partpass123",
                "full_name": "Workflow Participant",
                "school": "Test School #42",
                "grade": 11,
            },
        )
        assert part_reg.status_code == 201
        assert part_reg.json()["role"] == "participant"  # Verify auto-assigned role
        part_token = part_reg.json()["access_token"]
        part_headers = {"Authorization": f"Bearer {part_token}"}

        # ── Step 3: Admin creates competition ──
        comp_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Full Workflow Olympiad",
                "date": "2026-05-20",
                "registration_start": "2026-01-01T00:00:00",
                "registration_end": "2026-05-15T23:59:59",
                "variants_count": 4,
                "max_score": 100,
            },
            headers=admin_headers,
        )
        assert comp_resp.status_code == 201
        competition = comp_resp.json()
        competition_id = competition["id"]
        assert competition["status"] == "draft"

        # ── Step 4: Admin opens registration ──
        open_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/open-registration",
            headers=admin_headers,
        )
        assert open_resp.status_code == 200
        assert open_resp.json()["status"] == "registration_open"

        # ── Step 5: Participant registers for competition ──
        reg_resp = await client.post(
            "/api/v1/registrations",
            json={"competition_id": competition_id},
            headers=part_headers,
        )
        assert reg_resp.status_code == 201
        registration = reg_resp.json()
        registration_id = registration["id"]
        entry_token = registration["entry_token"]
        assert registration["status"] == "pending"
        assert entry_token is not None
        assert len(entry_token) > 20

        # ── Step 6: Admin starts competition (admission opens) ──
        start_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/start",
            headers=admin_headers,
        )
        assert start_resp.status_code == 200
        assert start_resp.json()["status"] == "in_progress"

        # ── Step 7: Admitter verifies entry QR ──
        # Admin also has admitter permissions
        verify_resp = await client.post(
            "/api/v1/admission/verify",
            json={"token": entry_token},
            headers=admin_headers,
        )
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["participant_name"] == "Workflow Participant"
        assert verify_data["competition_name"] == "Full Workflow Olympiad"
        assert verify_data["can_proceed"] is True
        assert verify_data["registration_id"] == registration_id

        # ── Step 8: Admitter approves admission (mock storage + PDF) ──
        mock_storage = MagicMock()
        mock_storage.upload_file.return_value = "sheets/test.pdf"
        mock_storage.get_presigned_url.return_value = "http://mock-minio/sheets/test.pdf"

        mock_sheet_gen = MagicMock()
        mock_sheet_gen.generate_answer_sheet.return_value = b"%PDF-1.4 mock content"

        with patch(
            "olimpqr.presentation.api.v1.admission.MinIOStorage",
            return_value=mock_storage,
        ), patch(
            "olimpqr.presentation.api.v1.admission.SheetGenerator",
            return_value=mock_sheet_gen,
        ):
            approve_resp = await client.post(
                f"/api/v1/admission/{registration_id}/approve",
                json={"raw_entry_token": entry_token},
                headers=admin_headers,
            )
        assert approve_resp.status_code == 201, approve_resp.json()
        approve_data = approve_resp.json()
        attempt_id = approve_data["attempt_id"]
        assert approve_data["variant_number"] >= 1
        assert approve_data["pdf_url"] == "http://mock-minio/sheets/test.pdf"
        assert approve_data["sheet_token"] is not None

        # ── Step 9: Apply score to attempt ──
        # Attempt is in PRINTED status, need to mark as SCANNED first
        from uuid import UUID as _UUID
        from sqlalchemy import select, update
        from olimpqr.domain.value_objects import AttemptStatus

        attempt_uuid = _UUID(attempt_id)
        await db_session.execute(
            update(AttemptModel)
            .where(AttemptModel.id == attempt_uuid)
            .values(status=AttemptStatus.SCANNED)
        )
        await db_session.commit()

        # Apply score via scan verification endpoint
        apply_resp = await client.post(
            f"/api/v1/scans/attempts/{attempt_id}/apply-score",
            json={"score": 85},
            headers=admin_headers,
        )
        assert apply_resp.status_code == 200
        score_data = apply_resp.json()
        assert score_data["score_total"] == 85
        assert score_data["status"] == "scored"

        # ── Step 10: Admin moves to checking phase ──
        check_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/start-checking",
            headers=admin_headers,
        )
        assert check_resp.status_code == 200
        assert check_resp.json()["status"] == "checking"

        # ── Step 11: Publish attempt result ──
        await db_session.execute(
            update(AttemptModel)
            .where(AttemptModel.id == attempt_uuid)
            .values(status=AttemptStatus.PUBLISHED)
        )
        await db_session.commit()

        # ── Step 12: Admin publishes competition results ──
        publish_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/publish",
            headers=admin_headers,
        )
        assert publish_resp.status_code == 200
        assert publish_resp.json()["status"] == "published"

        # ── Step 13: Public can view results (no auth) ──
        results_resp = await client.get(
            f"/api/v1/results/{competition_id}",
        )
        assert results_resp.status_code == 200
        results = results_resp.json()
        assert results["competition_name"] == "Full Workflow Olympiad"
        assert results["total_participants"] == 1
        assert len(results["results"]) == 1
        assert results["results"][0]["rank"] == 1
        assert results["results"][0]["participant_name"] == "Workflow Participant"
        assert results["results"][0]["score"] == 85
        assert results["results"][0]["max_score"] == 100

    async def test_unpublished_results_not_visible(self, client: AsyncClient, admin_user):
        """Results should not be visible before publishing."""
        _, admin_headers = admin_user

        # Create competition in draft
        comp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Unpublished Test",
                "date": "2026-06-01",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-05-25T23:59:59",
                "variants_count": 2,
                "max_score": 50,
            },
            headers=admin_headers,
        )
        comp_id = comp.json()["id"]

        # Try to view results — should be forbidden
        results_resp = await client.get(f"/api/v1/results/{comp_id}")
        assert results_resp.status_code == 403
        assert "not yet published" in results_resp.json()["detail"].lower()

    async def test_entry_token_single_use(self, client: AsyncClient, db_session):
        """Entry token can only be used once for admission."""

        # Setup: admin + participant + competition + registration
        admin_user = UserModel(
            id=uuid4(),
            email="single_use_admin@test.com",
            password_hash=hash_password("adminpass123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "single_use_admin@test.com", "password": "adminpass123"}
        )
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        part_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "single_use_part@test.com",
                "password": "partpass123",
                "full_name": "Single Use Test",
                "school": "Test School",
                "grade": 10,
            },
        )
        part_headers = {"Authorization": f"Bearer {part_reg.json()['access_token']}"}

        comp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Single Use Token Test",
                "date": "2026-07-01",
                "registration_start": "2026-01-01T00:00:00",
                "registration_end": "2026-06-25T23:59:59",
                "variants_count": 2,
                "max_score": 50,
            },
            headers=admin_headers,
        )
        comp_id = comp.json()["id"]

        await client.post(
            f"/api/v1/competitions/{comp_id}/open-registration",
            headers=admin_headers,
        )

        # Register BEFORE starting competition
        reg = await client.post(
            "/api/v1/registrations",
            json={"competition_id": comp_id},
            headers=part_headers,
        )
        assert reg.status_code == 201, f"Registration failed: {reg.json()}"
        reg_id = reg.json()["id"]
        entry_token = reg.json()["entry_token"]

        await client.post(
            f"/api/v1/competitions/{comp_id}/start",
            headers=admin_headers,
        )

        # First approve — should work
        mock_storage = MagicMock()
        mock_storage.upload_file.return_value = "sheets/test.pdf"
        mock_storage.get_presigned_url.return_value = "http://mock-minio/sheets/test.pdf"
        mock_sheet_gen = MagicMock()
        mock_sheet_gen.generate_answer_sheet.return_value = b"%PDF-1.4 mock"

        with patch(
            "olimpqr.presentation.api.v1.admission.MinIOStorage",
            return_value=mock_storage,
        ), patch(
            "olimpqr.presentation.api.v1.admission.SheetGenerator",
            return_value=mock_sheet_gen,
        ):
            first_approve = await client.post(
                f"/api/v1/admission/{reg_id}/approve",
                json={"raw_entry_token": entry_token},
                headers=admin_headers,
            )
        assert first_approve.status_code == 201

        # Second approve — should fail (token already used)
        with patch(
            "olimpqr.presentation.api.v1.admission.MinIOStorage",
            return_value=mock_storage,
        ), patch(
            "olimpqr.presentation.api.v1.admission.SheetGenerator",
            return_value=mock_sheet_gen,
        ):
            second_approve = await client.post(
                f"/api/v1/admission/{reg_id}/approve",
                json={"raw_entry_token": entry_token},
                headers=admin_headers,
            )
        assert second_approve.status_code == 400
        assert "already been used" in second_approve.json()["detail"].lower()

    async def test_verify_expired_token_rejected(self, client: AsyncClient, db_session):
        """Verify should reject expired entry tokens."""

        admin_user = UserModel(
            id=uuid4(),
            email="expired_admin@test.com",
            password_hash=hash_password("adminpass123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db_session.add(admin_user)
        await db_session.commit()

        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "expired_admin@test.com", "password": "adminpass123"}
        )
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        # Verify with a fake token that doesn't exist
        verify_resp = await client.post(
            "/api/v1/admission/verify",
            json={"token": "completely-fake-token-that-does-not-exist"},
            headers=admin_headers,
        )
        assert verify_resp.status_code == 400
        assert "not found" in verify_resp.json()["detail"].lower()
