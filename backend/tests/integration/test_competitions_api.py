"""Integration tests for competitions API endpoints."""

import pytest
from httpx import AsyncClient

from .conftest import make_auth_header
from olimpqr.domain.value_objects import UserRole


@pytest.mark.integration
class TestCreateCompetition:
    """Tests for POST /api/v1/competitions."""

    async def test_create_competition_admin(self, client: AsyncClient, admin_user):
        """Admin can create a competition."""
        _, headers = admin_user
        response = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Math Olympiad 2026",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 4,
                "max_score": 100,
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Math Olympiad 2026"
        assert data["status"] == "draft"
        assert data["variants_count"] == 4
        assert data["max_score"] == 100

    async def test_create_competition_participant_forbidden(self, client: AsyncClient, participant_user):
        """Participant cannot create a competition."""
        _, _, headers = participant_user
        response = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Test",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 1,
                "max_score": 50,
            },
            headers=headers,
        )
        assert response.status_code == 403

    async def test_create_competition_no_auth(self, client: AsyncClient):
        """Unauthenticated request should fail."""
        response = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Test",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 1,
                "max_score": 50,
            },
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestListCompetitions:
    """Tests for GET /api/v1/competitions."""

    async def test_list_competitions_public(self, client: AsyncClient):
        """List competitions is public (no auth required)."""
        response = await client.get("/api/v1/competitions")
        assert response.status_code == 200
        data = response.json()
        assert "competitions" in data
        assert "total" in data

    async def test_list_competitions_with_data(self, client: AsyncClient, admin_user):
        """List competitions returns created items."""
        _, headers = admin_user
        # Create two competitions
        for name in ["Comp A", "Comp B"]:
            await client.post(
                "/api/v1/competitions",
                json={
                    "name": name,
                    "date": "2026-03-15",
                    "registration_start": "2026-02-01T00:00:00",
                    "registration_end": "2026-03-10T23:59:59",
                    "variants_count": 2,
                    "max_score": 100,
                },
                headers=headers,
            )

        response = await client.get("/api/v1/competitions")
        data = response.json()
        assert data["total"] == 2
        names = {c["name"] for c in data["competitions"]}
        assert "Comp A" in names
        assert "Comp B" in names


@pytest.mark.integration
class TestGetCompetition:
    """Tests for GET /api/v1/competitions/{id}."""

    async def test_get_competition_success(self, client: AsyncClient, admin_user):
        """Get competition by ID."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Get Test",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 2,
                "max_score": 80,
            },
            headers=headers,
        )
        comp_id = create_resp.json()["id"]

        response = await client.get(f"/api/v1/competitions/{comp_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"
        assert response.json()["max_score"] == 80

    async def test_get_competition_not_found(self, client: AsyncClient):
        """Get non-existent competition should return 404."""
        response = await client.get(
            "/api/v1/competitions/00000000-0000-0000-0000-000000000000"
        )
        assert response.status_code == 404


@pytest.mark.integration
class TestUpdateCompetition:
    """Tests for PUT /api/v1/competitions/{id}."""

    async def test_update_competition(self, client: AsyncClient, admin_user):
        """Admin can update competition fields."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Original",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 2,
                "max_score": 50,
            },
            headers=headers,
        )
        comp_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/competitions/{comp_id}",
            json={"name": "Updated", "max_score": 120},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated"
        assert response.json()["max_score"] == 120


@pytest.mark.integration
class TestDeleteCompetition:
    """Tests for DELETE /api/v1/competitions/{id}."""

    async def test_delete_competition(self, client: AsyncClient, admin_user):
        """Admin can delete a competition."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "To Delete",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 1,
                "max_score": 50,
            },
            headers=headers,
        )
        comp_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/competitions/{comp_id}",
            headers=headers,
        )
        assert response.status_code == 204

        # Verify deleted
        get_resp = await client.get(f"/api/v1/competitions/{comp_id}")
        assert get_resp.status_code == 404


@pytest.mark.integration
class TestCompetitionStatusTransitions:
    """Tests for competition status change endpoints."""

    async def test_full_lifecycle(self, client: AsyncClient, admin_user):
        """Test full competition status lifecycle: draft -> open -> in_progress -> checking -> published."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Lifecycle Test",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 2,
                "max_score": 100,
            },
            headers=headers,
        )
        comp_id = create_resp.json()["id"]
        assert create_resp.json()["status"] == "draft"

        # Open registration
        resp = await client.post(
            f"/api/v1/competitions/{comp_id}/open-registration",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "registration_open"

        # Start competition
        resp = await client.post(
            f"/api/v1/competitions/{comp_id}/start",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "in_progress"

        # Start checking
        resp = await client.post(
            f"/api/v1/competitions/{comp_id}/start-checking",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "checking"

        # Publish results
        resp = await client.post(
            f"/api/v1/competitions/{comp_id}/publish",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "published"
