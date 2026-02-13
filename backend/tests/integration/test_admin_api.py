"""Integration tests for admin API endpoints."""

import pytest
from httpx import AsyncClient

from .conftest import make_auth_header
from olimpqr.domain.value_objects import UserRole


@pytest.mark.integration
class TestListUsers:
    """Tests for GET /api/v1/admin/users."""

    async def test_list_users_admin(self, client: AsyncClient, admin_user):
        """Admin can list all users."""
        _, headers = admin_user
        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1  # At least the admin

    async def test_list_users_forbidden_for_participant(self, client: AsyncClient, participant_user):
        """Participant cannot list users."""
        _, _, headers = participant_user
        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403

    async def test_list_users_no_auth(self, client: AsyncClient):
        """Unauthenticated request should fail."""
        response = await client.get("/api/v1/admin/users")
        assert response.status_code == 401


@pytest.mark.integration
class TestCreateStaffUser:
    """Tests for POST /api/v1/admin/users."""

    async def test_create_admitter(self, client: AsyncClient, admin_user):
        """Admin can create an admitter user."""
        _, headers = admin_user
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "admitter@test.com",
                "password": "admitter123",
                "role": "admitter",
            },
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "admitter@test.com"
        assert data["role"] == "admitter"
        assert data["is_active"] is True

    async def test_create_scanner(self, client: AsyncClient, admin_user):
        """Admin can create a scanner user."""
        _, headers = admin_user
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "scanner@test.com",
                "password": "scanner123",
                "role": "scanner",
            },
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["role"] == "scanner"

    async def test_create_duplicate_email(self, client: AsyncClient, admin_user):
        """Creating user with existing email should fail."""
        _, headers = admin_user
        payload = {
            "email": "dup@test.com",
            "password": "password123",
            "role": "scanner",
        }
        await client.post("/api/v1/admin/users", json=payload, headers=headers)
        response = await client.post("/api/v1/admin/users", json=payload, headers=headers)
        assert response.status_code == 400


@pytest.mark.integration
class TestUpdateUser:
    """Tests for PUT /api/v1/admin/users/{id}."""

    async def test_deactivate_user(self, client: AsyncClient, admin_user):
        """Admin can deactivate a user."""
        _, headers = admin_user
        # Create user
        create_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "todeactivate@test.com",
                "password": "password123",
                "role": "scanner",
            },
            headers=headers,
        )
        user_id = create_resp.json()["id"]

        # Deactivate
        response = await client.put(
            f"/api/v1/admin/users/{user_id}",
            json={"is_active": False},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    async def test_change_role(self, client: AsyncClient, admin_user):
        """Admin can change user role."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "changerole@test.com",
                "password": "password123",
                "role": "scanner",
            },
            headers=headers,
        )
        user_id = create_resp.json()["id"]

        response = await client.put(
            f"/api/v1/admin/users/{user_id}",
            json={"role": "admitter"},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admitter"


@pytest.mark.integration
class TestDeleteUser:
    """Tests for DELETE /api/v1/admin/users/{id}."""

    async def test_soft_delete_user(self, client: AsyncClient, admin_user):
        """Admin can soft-delete (deactivate) a user."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/admin/users",
            json={
                "email": "todelete@test.com",
                "password": "password123",
                "role": "scanner",
            },
            headers=headers,
        )
        user_id = create_resp.json()["id"]

        response = await client.delete(
            f"/api/v1/admin/users/{user_id}",
            headers=headers,
        )
        assert response.status_code == 204

    async def test_cannot_delete_self(self, client: AsyncClient, admin_user):
        """Admin cannot deactivate their own account."""
        user, headers = admin_user
        response = await client.delete(
            f"/api/v1/admin/users/{user.id}",
            headers=headers,
        )
        assert response.status_code == 400


@pytest.mark.integration
class TestAuditLog:
    """Tests for GET /api/v1/admin/audit-log."""

    async def test_get_audit_log(self, client: AsyncClient, admin_user):
        """Admin can view audit log."""
        _, headers = admin_user
        response = await client.get("/api/v1/admin/audit-log", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
