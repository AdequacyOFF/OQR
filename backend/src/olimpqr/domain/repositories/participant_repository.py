"""Participant repository interface."""

from abc import abstractmethod
from uuid import UUID

from .base import BaseRepository
from ..entities import Participant


class ParticipantRepository(BaseRepository[Participant]):
    """Repository interface for Participant entity."""

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Participant | None:
        """Get participant by user ID."""
        pass
