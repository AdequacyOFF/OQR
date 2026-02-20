"""Integration tests for rooms API."""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .conftest import make_auth_header, CompetitionModel
from olimpqr.domain.value_objects import UserRole, CompetitionStatus


@pytest.mark.asyncio
class TestRoomsAPI:
    async def _create_competition(self, db_session: AsyncSession, admin_id):
        comp = CompetitionModel(
            id=uuid4(),
            name="Test Olympiad",
            date=datetime.utcnow().date(),
            registration_start=datetime.utcnow(),
            registration_end=datetime.utcnow() + timedelta(days=7),
            variants_count=4,
            max_score=100,
            status=CompetitionStatus.IN_PROGRESS,
            created_by=admin_id,
        )
        db_session.add(comp)
        await db_session.commit()
        return comp

    async def test_create_room(self, client: AsyncClient, admin_user, db_session):
        user, headers = admin_user
        comp = await self._create_competition(db_session, user.id)

        response = await client.post(
            f"/api/v1/rooms/{comp.id}",
            json={"name": "Room 301", "capacity": 30},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Room 301"
        assert data["capacity"] == 30

    async def test_list_rooms(self, client: AsyncClient, admin_user, db_session):
        user, headers = admin_user
        comp = await self._create_competition(db_session, user.id)

        await client.post(f"/api/v1/rooms/{comp.id}", json={"name": "R1", "capacity": 20}, headers=headers)
        await client.post(f"/api/v1/rooms/{comp.id}", json={"name": "R2", "capacity": 30}, headers=headers)

        response = await client.get(f"/api/v1/rooms/{comp.id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["rooms"]) == 2

    async def test_delete_room(self, client: AsyncClient, admin_user, db_session):
        user, headers = admin_user
        comp = await self._create_competition(db_session, user.id)

        resp = await client.post(f"/api/v1/rooms/{comp.id}", json={"name": "To Delete", "capacity": 10}, headers=headers)
        room_id = resp.json()["id"]

        response = await client.delete(f"/api/v1/rooms/room/{room_id}", headers=headers)
        assert response.status_code == 204
