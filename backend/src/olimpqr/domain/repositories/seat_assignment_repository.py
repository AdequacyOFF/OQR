"""Seat assignment repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import SeatAssignment


class SeatAssignmentRepository(BaseRepository[SeatAssignment]):
    """Repository interface for SeatAssignment entity."""

    @abstractmethod
    async def get_by_registration(self, registration_id: UUID) -> SeatAssignment | None:
        """Get seat assignment by registration ID."""
        pass

    @abstractmethod
    async def get_by_room(self, room_id: UUID) -> List[SeatAssignment]:
        """Get all seat assignments for a room."""
        pass

    @abstractmethod
    async def count_by_room(self, room_id: UUID) -> int:
        """Count occupied seats in a room."""
        pass

    @abstractmethod
    async def count_by_room_and_institution(self, room_id: UUID, institution_id: UUID) -> int:
        """Count participants from a given institution in a room."""
        pass
