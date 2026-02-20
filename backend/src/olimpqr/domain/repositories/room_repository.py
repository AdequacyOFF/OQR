"""Room repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Room


class RoomRepository(BaseRepository[Room]):
    """Repository interface for Room entity."""

    @abstractmethod
    async def get_by_competition(self, competition_id: UUID) -> List[Room]:
        """Get all rooms for a competition."""
        pass
