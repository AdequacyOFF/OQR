"""Integration tests for auth API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_participant_success(self, client: AsyncClient):
        """Register a new participant with all required fields (new flow)."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "securepass123",
                "full_name": "Test User",
                "school": "Test School",
                "grade": 10,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["email"] == "new@example.com"
        assert data["role"] == "participant"  # Auto-assigned

    async def test_register_role_field_ignored(self, client: AsyncClient):
        """Role field in registration should be ignored (always participant)."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "role.test@example.com",
                "password": "securepass123",
                "role": "admin",  # Try to escalate privileges
                "full_name": "Role Test",
                "school": "Test School",
                "grade": 10,
            },
        )
        # Should either succeed with participant role or return 422 (extra field)
        if response.status_code == 201:
            data = response.json()
            assert data["role"] == "participant", "Role escalation vulnerability!"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Registering with existing email should fail."""
        payload = {
            "email": "dup@example.com",
            "password": "securepass123",
            "full_name": "Dup User",
            "school": "Test School",
            "grade": 9,
        }
        await client.post("/api/v1/auth/register", json=payload)
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_register_participant_missing_fields(self, client: AsyncClient):
        """Participant registration without required fields should fail."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "missing@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 422  # Pydantic validation for missing fields

    async def test_register_short_password(self, client: AsyncClient):
        """Password shorter than 8 chars should be rejected."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "abc",
                "full_name": "Short Pass",
                "school": "Test School",
                "grade": 10,
            },
        )
        assert response.status_code == 422  # Pydantic validation


@pytest.mark.integration
class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient):
        """Login with valid credentials."""
        # Register first (as participant)
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "securepass123",
                "full_name": "Login Test",
                "school": "Test School",
                "grade": 10,
            },
        )
        # Login
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "login@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == "login@example.com"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Login with wrong password should fail."""
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@example.com",
                "password": "securepass123",
                "full_name": "Wrong Pass",
                "school": "Test School",
                "grade": 10,
            },
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login with non-existent email should fail."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nobody@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 401


@pytest.mark.integration
class TestGetMe:
    """Tests for GET /api/v1/auth/me."""

    async def test_get_me_authenticated(self, client: AsyncClient):
        """Get current user with valid token."""
        # Register and get token (as participant)
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "password": "securepass123",
                "full_name": "Me Test",
                "school": "Test School",
                "grade": 11,
            },
        )
        token = reg.json()["access_token"]

        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me@example.com"
        assert data["role"] == "participant"  # Auto-assigned role
        assert data["is_active"] is True

    async def test_get_me_no_token(self, client: AsyncClient):
        """Access /me without token should fail."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Access /me with invalid token should fail."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401
