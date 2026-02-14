"""Registration repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Registration


class RegistrationRepository(BaseRepository[Registration]):
    """Repository interface for Registration entity."""

    @abstractmethod
    async def get_by_participant_and_competition(
        self, participant_id: UUID, competition_id: UUID
    ) -> Registration | None:
        """Get registration by participant and competition."""
        pass

    @abstractmethod
    async def get_by_competition(
        self, competition_id: UUID, skip: int = 0, limit: int = 1000
    ) -> List[Registration]:
        """Get all registrations for a competition."""
        pass

    @abstractmethod
    async def get_by_participant_id(
        self, participant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Registration]:
        """Get all registrations for a participant."""
        pass
