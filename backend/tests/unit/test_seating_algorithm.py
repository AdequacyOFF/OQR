"""Unit tests for the seating assignment algorithm."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from olimpqr.domain.entities import Room, SeatAssignment, Participant, Registration
from olimpqr.application.use_cases.seating.assign_seat import AssignSeatUseCase


@pytest.mark.asyncio
class TestSeatingAlgorithm:
    def _make_room(self, capacity=30, name="R1"):
        return Room(id=uuid4(), competition_id=uuid4(), name=name, capacity=capacity)

    def _make_participant(self, institution_id=None):
        return Participant(
            user_id=uuid4(),
            full_name="Test",
            school="School",
            grade=10,
            institution_id=institution_id,
        )

    def _make_registration(self, participant_id):
        return Registration(
            id=uuid4(),
            participant_id=participant_id,
            competition_id=uuid4(),
        )

    async def test_assigns_to_room_with_fewest_same_institution(self):
        inst_id = uuid4()
        room1 = self._make_room(name="R1")
        room2 = self._make_room(name="R2")
        participant = self._make_participant(institution_id=inst_id)
        registration = self._make_registration(participant.id)

        room_repo = AsyncMock()
        room_repo.get_by_competition.return_value = [room1, room2]
        room_repo.get_by_id.return_value = room2

        seat_repo = AsyncMock()
        seat_repo.get_by_registration.return_value = None
        seat_repo.count_by_room.side_effect = [5, 5]  # both have 5 occupied
        seat_repo.count_by_room_and_institution.side_effect = [3, 1]  # room1 has 3 same inst, room2 has 1
        seat_repo.get_by_room.return_value = []
        seat_repo.create.return_value = None

        reg_repo = AsyncMock()
        reg_repo.get_by_id.return_value = registration

        part_repo = AsyncMock()
        part_repo.get_by_id.return_value = participant

        uc = AssignSeatUseCase(room_repo, seat_repo, reg_repo, part_repo)
        result = await uc.execute(registration.id, uuid4(), variants_count=4)

        assert result is not None
        assert result.room_id == room2.id  # picked room2 (fewer same-inst)

    async def test_idempotent_returns_existing(self):
        existing = SeatAssignment(
            registration_id=uuid4(), room_id=uuid4(),
            seat_number=3, variant_number=2,
        )

        room_repo = AsyncMock()
        room_repo.get_by_id.return_value = Room(
            id=existing.room_id, competition_id=uuid4(), name="R1", capacity=30
        )

        seat_repo = AsyncMock()
        seat_repo.get_by_registration.return_value = existing

        reg_repo = AsyncMock()
        part_repo = AsyncMock()

        uc = AssignSeatUseCase(room_repo, seat_repo, reg_repo, part_repo)
        result = await uc.execute(existing.registration_id, uuid4(), variants_count=4)

        assert result.seat_number == 3
        assert result.variant_number == 2

    async def test_returns_none_if_no_rooms(self):
        registration = self._make_registration(uuid4())
        participant = self._make_participant()

        room_repo = AsyncMock()
        room_repo.get_by_competition.return_value = []

        seat_repo = AsyncMock()
        seat_repo.get_by_registration.return_value = None

        reg_repo = AsyncMock()
        reg_repo.get_by_id.return_value = registration

        part_repo = AsyncMock()
        part_repo.get_by_id.return_value = participant

        uc = AssignSeatUseCase(room_repo, seat_repo, reg_repo, part_repo)
        result = await uc.execute(registration.id, uuid4(), variants_count=4)

        assert result is None

    async def test_variant_assignment(self):
        """Test variant = (seat_number % variants_count) + 1."""
        room = self._make_room(capacity=100)
        participant = self._make_participant()
        registration = self._make_registration(participant.id)

        room_repo = AsyncMock()
        room_repo.get_by_competition.return_value = [room]
        room_repo.get_by_id.return_value = room

        seat_repo = AsyncMock()
        seat_repo.get_by_registration.return_value = None
        seat_repo.count_by_room.return_value = 0
        seat_repo.count_by_room_and_institution.return_value = 0
        seat_repo.get_by_room.return_value = []
        seat_repo.create.return_value = None

        reg_repo = AsyncMock()
        reg_repo.get_by_id.return_value = registration

        part_repo = AsyncMock()
        part_repo.get_by_id.return_value = participant

        uc = AssignSeatUseCase(room_repo, seat_repo, reg_repo, part_repo)
        result = await uc.execute(registration.id, uuid4(), variants_count=4)

        assert result is not None
        assert result.seat_number == 1
        assert result.variant_number == (1 % 4) + 1  # = 2
