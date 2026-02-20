"""Participant event repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import ParticipantEvent


class ParticipantEventRepository(BaseRepository[ParticipantEvent]):
    """Repository interface for ParticipantEvent entity."""

    @abstractmethod
    async def get_by_attempt(self, attempt_id: UUID) -> List[ParticipantEvent]:
        """Get all events for an attempt."""
        pass
