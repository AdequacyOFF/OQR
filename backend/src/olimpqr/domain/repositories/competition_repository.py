"""Competition repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Competition
from ..value_objects import CompetitionStatus


class CompetitionRepository(BaseRepository[Competition]):
    """Repository interface for Competition entity."""

    @abstractmethod
    async def get_by_status(self, status: CompetitionStatus, skip: int = 0, limit: int = 100) -> List[Competition]:
        """Get competitions by status."""
        pass

    @abstractmethod
    async def get_published(self, skip: int = 0, limit: int = 100) -> List[Competition]:
        """Get published competitions."""
        pass
