"""Integration tests for health check, CORS, and security basics."""

import pytest
from httpx import AsyncClient

from .conftest import make_auth_header
from olimpqr.domain.value_objects import UserRole


@pytest.mark.integration
class TestHealthCheck:
    """Tests for GET /health."""

    async def test_health_check(self, client: AsyncClient):
        """Health check should always return 200."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "environment" in data


@pytest.mark.integration
class TestRoleBasedAccess:
    """Tests for role-based access control across endpoints."""

    async def test_participant_cannot_access_admin(self, client: AsyncClient, participant_user):
        """Participant cannot access admin endpoints."""
        _, _, headers = participant_user
        response = await client.get("/api/v1/admin/users", headers=headers)
        assert response.status_code == 403

    async def test_participant_cannot_access_scanner(self, client: AsyncClient, participant_user):
        """Participant cannot access scanner endpoints."""
        _, _, headers = participant_user
        response = await client.get("/api/v1/scans", headers=headers)
        assert response.status_code == 403

    async def test_expired_token_rejected(self, client: AsyncClient):
        """Expired JWT should be rejected."""
        from datetime import timedelta
        from olimpqr.infrastructure.security import create_access_token
        from uuid import uuid4

        token = create_access_token(
            user_id=uuid4(),
            email="expired@test.com",
            role=UserRole.ADMIN,
            expires_delta=timedelta(seconds=-1),  # Already expired
        )
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    async def test_malformed_token_rejected(self, client: AsyncClient):
        """Malformed JWT should be rejected."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.valid.jwt"},
        )
        assert response.status_code == 401

    async def test_missing_auth_header(self, client: AsyncClient):
        """Requests to protected endpoints without auth header should fail."""
        protected_endpoints = [
            ("GET", "/api/v1/auth/me"),
            ("POST", "/api/v1/competitions"),
            ("GET", "/api/v1/admin/users"),
            ("GET", "/api/v1/scans"),
        ]
        for method, path in protected_endpoints:
            response = await client.request(method, path)
            assert response.status_code == 401, f"Expected 401 for {method} {path}, got {response.status_code}"


@pytest.mark.integration
class TestPublicEndpoints:
    """Tests for endpoints that should be accessible without auth."""

    async def test_list_competitions_public(self, client: AsyncClient):
        """Competitions list should be public."""
        response = await client.get("/api/v1/competitions")
        assert response.status_code == 200

    async def test_get_competition_public(self, client: AsyncClient, admin_user):
        """Individual competition should be publicly accessible."""
        _, headers = admin_user
        create_resp = await client.post(
            "/api/v1/competitions",
            json={
                "name": "Public Test",
                "date": "2026-03-15",
                "registration_start": "2026-02-01T00:00:00",
                "registration_end": "2026-03-10T23:59:59",
                "variants_count": 2,
                "max_score": 100,
            },
            headers=headers,
        )
        comp_id = create_resp.json()["id"]

        # No auth header
        response = await client.get(f"/api/v1/competitions/{comp_id}")
        assert response.status_code == 200
