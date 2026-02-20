"""Integration tests for invigilator API."""

import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .conftest import (
    make_auth_header,
    CompetitionModel,
    RegistrationModel,
    AttemptModel,
)
from olimpqr.domain.value_objects import (
    UserRole, CompetitionStatus, RegistrationStatus, AttemptStatus,
)


@pytest.mark.asyncio
class TestInvigilatorAPI:
    async def _setup_attempt(self, db_session: AsyncSession, admin_id, participant_id):
        """Create competition + registration + attempt for testing."""
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

        reg = RegistrationModel(
            id=uuid4(),
            participant_id=participant_id,
            competition_id=comp.id,
            status=RegistrationStatus.ADMITTED,
        )
        db_session.add(reg)

        attempt = AttemptModel(
            id=uuid4(),
            registration_id=reg.id,
            variant_number=1,
            sheet_token_hash="a" * 64,
            status=AttemptStatus.PRINTED,
        )
        db_session.add(attempt)
        await db_session.commit()
        return attempt

    async def test_record_event(self, client: AsyncClient, invigilator_user, admin_user, participant_user, db_session):
        admin, _ = admin_user
        _, participant, _ = participant_user
        attempt = await self._setup_attempt(db_session, admin.id, participant.id)
        _, headers = invigilator_user

        response = await client.post(
            "/api/v1/invigilator/events",
            json={"attempt_id": str(attempt.id), "event_type": "start_work"},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["event_type"] == "start_work"

    async def test_get_attempt_events(self, client: AsyncClient, invigilator_user, admin_user, participant_user, db_session):
        admin, _ = admin_user
        _, participant, _ = participant_user
        attempt = await self._setup_attempt(db_session, admin.id, participant.id)
        _, headers = invigilator_user

        # Record two events
        await client.post(
            "/api/v1/invigilator/events",
            json={"attempt_id": str(attempt.id), "event_type": "start_work"},
            headers=headers,
        )
        await client.post(
            "/api/v1/invigilator/events",
            json={"attempt_id": str(attempt.id), "event_type": "exit_room"},
            headers=headers,
        )

        response = await client.get(
            f"/api/v1/invigilator/attempt/{attempt.id}/events",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["events"]) == 2

    async def test_record_event_invalid_attempt(self, client: AsyncClient, invigilator_user):
        _, headers = invigilator_user
        response = await client.post(
            "/api/v1/invigilator/events",
            json={"attempt_id": str(uuid4()), "event_type": "start_work"},
            headers=headers,
        )
        assert response.status_code == 400

    async def test_record_event_requires_invigilator(self, client: AsyncClient, participant_user):
        _, _, headers = participant_user
        response = await client.post(
            "/api/v1/invigilator/events",
            json={"attempt_id": str(uuid4()), "event_type": "start_work"},
            headers=headers,
        )
        assert response.status_code == 403
