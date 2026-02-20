"""Integration tests for institutions API."""

import pytest
import pytest_asyncio
from httpx import AsyncClient

from .conftest import make_auth_header


@pytest.mark.asyncio
class TestInstitutionsAPI:
    async def test_create_institution(self, client: AsyncClient, admin_user):
        _, headers = admin_user
        response = await client.post(
            "/api/v1/institutions",
            json={"name": "School #1", "short_name": "S1", "city": "Moscow"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "School #1"
        assert data["short_name"] == "S1"
        assert data["city"] == "Moscow"

    async def test_create_duplicate_institution(self, client: AsyncClient, admin_user):
        _, headers = admin_user
        await client.post(
            "/api/v1/institutions",
            json={"name": "Duplicate School"},
            headers=headers,
        )
        response = await client.post(
            "/api/v1/institutions",
            json={"name": "Duplicate School"},
            headers=headers,
        )
        assert response.status_code == 400

    async def test_list_institutions(self, client: AsyncClient, admin_user):
        _, headers = admin_user
        await client.post("/api/v1/institutions", json={"name": "A School"}, headers=headers)
        await client.post("/api/v1/institutions", json={"name": "B School"}, headers=headers)

        response = await client.get("/api/v1/institutions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    async def test_search_institutions(self, client: AsyncClient, admin_user):
        _, headers = admin_user
        await client.post("/api/v1/institutions", json={"name": "Математическая гимназия"}, headers=headers)

        response = await client.get("/api/v1/institutions/search?q=Математ")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Математическая" in data[0]["name"]

    async def test_delete_institution(self, client: AsyncClient, admin_user):
        _, headers = admin_user
        resp = await client.post("/api/v1/institutions", json={"name": "To Delete"}, headers=headers)
        inst_id = resp.json()["id"]

        response = await client.delete(f"/api/v1/institutions/{inst_id}", headers=headers)
        assert response.status_code == 204

    async def test_create_institution_requires_admin(self, client: AsyncClient, participant_user):
        _, _, headers = participant_user
        response = await client.post(
            "/api/v1/institutions",
            json={"name": "Test School"},
            headers=headers,
        )
        assert response.status_code == 403
