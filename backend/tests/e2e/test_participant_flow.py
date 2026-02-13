"""E2E test: Complete participant registration flow.

This test covers the full participant journey:
1. Register as participant
2. Login
3. View available competitions
4. Register for a competition
5. Get entry QR code
"""

import pytest
from httpx import AsyncClient


@pytest.mark.e2e
class TestParticipantRegistrationFlow:
    """Full E2E test for participant registration workflow."""

    async def test_complete_participant_flow(self, client: AsyncClient, admin_user):
        """Test complete participant journey from registration to entry QR."""

        # Step 1: Admin creates a competition
        _, admin_headers = admin_user
        competition_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "E2E Test Olympiad",
                "date": "2026-04-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-04-10T23:59:59",
                "variants_count": 4,
                "max_score": 100,
            },
            headers=admin_headers,
        )
        assert competition_resp.status_code == 201
        competition_id = competition_resp.json()["id"]

        # Step 2: Admin opens registration
        open_resp = await client.post(
            f"/api/v1/competitions/{competition_id}/open-registration",
            headers=admin_headers,
        )
        assert open_resp.status_code == 200
        assert open_resp.json()["status"] == "registration_open"

        # Step 3: Participant registers account
        participant_email = "e2e_participant@test.com"
        register_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": participant_email,
                "password": "securepass123",
                "role": "participant",
                "full_name": "E2E Test Participant",
                "school": "Test School #1",
                "grade": 11,
            },
        )
        assert register_resp.status_code == 201
        participant_token = register_resp.json()["access_token"]
        participant_headers = {"Authorization": f"Bearer {participant_token}"}

        # Step 4: Participant views competitions
        list_resp = await client.get("/api/v1/competitions")
        assert list_resp.status_code == 200
        competitions = list_resp.json()["competitions"]
        assert any(c["id"] == competition_id for c in competitions)

        # Step 5: Participant views competition details
        detail_resp = await client.get(f"/api/v1/competitions/{competition_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["name"] == "E2E Test Olympiad"
        assert detail_resp.json()["status"] == "registration_open"

        # Step 6: Participant registers for competition
        reg_resp = await client.post(
            "/api/v1/registrations",
            json={"competition_id": competition_id},
            headers=participant_headers,
        )
        assert reg_resp.status_code == 201
        registration_data = reg_resp.json()
        assert registration_data["competition_id"] == competition_id
        assert registration_data["status"] == "pending"
        # Entry token is returned only on creation
        assert "entry_token" in registration_data
        entry_token = registration_data["entry_token"]
        assert entry_token is not None
        assert len(entry_token) > 20  # Token should have significant length

        # Step 7: Verify participant can check their registration
        me_resp = await client.get("/api/v1/auth/me", headers=participant_headers)
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == participant_email
        assert me_resp.json()["role"] == "participant"

    async def test_participant_cannot_register_twice(self, client: AsyncClient, admin_user):
        """Participant cannot register for the same competition twice."""

        # Setup: Create competition and open registration
        _, admin_headers = admin_user
        comp_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Double Registration Test",
                "date": "2026-05-01",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-04-25T23:59:59",
                "variants_count": 2,
                "max_score": 50,
            },
            headers=admin_headers,
        )
        competition_id = comp_resp.json()["id"]
        await client.post(
            f"/api/v1/competitions/{competition_id}/open-registration",
            headers=admin_headers,
        )

        # Register participant
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "double_reg@test.com",
                "password": "securepass123",
                "role": "participant",
                "full_name": "Double Reg User",
                "school": "Test School",
                "grade": 10,
            },
        )
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # First registration - should succeed
        first_reg = await client.post(
            "/api/v1/registrations",
            json={"competition_id": competition_id},
            headers=headers,
        )
        assert first_reg.status_code == 201

        # Second registration - should fail
        second_reg = await client.post(
            "/api/v1/registrations",
            json={"competition_id": competition_id},
            headers=headers,
        )
        assert second_reg.status_code == 400
        assert "already registered" in second_reg.json()["detail"].lower()

    async def test_participant_cannot_register_closed_competition(
        self, client: AsyncClient, admin_user
    ):
        """Participant cannot register for a competition that is not open."""

        # Create competition but don't open registration (stays in draft)
        _, admin_headers = admin_user
        comp_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Closed Competition Test",
                "date": "2026-06-01",
                "registration_start": "2026-05-01T00:00:00",
                "registration_end": "2026-05-25T23:59:59",
                "variants_count": 2,
                "max_score": 100,
            },
            headers=admin_headers,
        )
        competition_id = comp_resp.json()["id"]
        # Note: NOT opening registration

        # Register participant
        reg_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "closed_comp@test.com",
                "password": "securepass123",
                "role": "participant",
                "full_name": "Closed Test User",
                "school": "Test School",
                "grade": 9,
            },
        )
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to register - should fail
        reg_attempt = await client.post(
            "/api/v1/registrations",
            json={"competition_id": competition_id},
            headers=headers,
        )
        assert reg_attempt.status_code == 400
        assert "not open" in reg_attempt.json()["detail"].lower()
