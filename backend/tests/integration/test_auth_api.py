"""Integration tests for auth API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestRegister:
    """Tests for POST /api/v1/auth/register."""

    async def test_register_participant_success(self, client: AsyncClient):
        """Register a new participant with all required fields."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "securepass123",
                "role": "participant",
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
        assert data["role"] == "participant"

    async def test_register_admin_success(self, client: AsyncClient):
        """Register an admin user (no participant fields needed)."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "admin@example.com",
                "password": "securepass123",
                "role": "admin",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "admin"

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Registering with existing email should fail."""
        payload = {
            "email": "dup@example.com",
            "password": "securepass123",
            "role": "admin",
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
                "role": "participant",
            },
        )
        assert response.status_code == 400

    async def test_register_short_password(self, client: AsyncClient):
        """Password shorter than 8 chars should be rejected."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@example.com",
                "password": "abc",
                "role": "admin",
            },
        )
        assert response.status_code == 422  # Pydantic validation


@pytest.mark.integration
class TestLogin:
    """Tests for POST /api/v1/auth/login."""

    async def test_login_success(self, client: AsyncClient):
        """Login with valid credentials."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@example.com",
                "password": "securepass123",
                "role": "admin",
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
                "role": "admin",
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
        # Register and get token
        reg = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "me@example.com",
                "password": "securepass123",
                "role": "admin",
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
        assert data["role"] == "admin"
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
