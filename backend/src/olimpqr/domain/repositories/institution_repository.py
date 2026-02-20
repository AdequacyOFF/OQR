"""Institution repository interface."""

from abc import abstractmethod
from typing import List

from .base import BaseRepository
from ..entities import Institution


class InstitutionRepository(BaseRepository[Institution]):
    """Repository interface for Institution entity."""

    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> List[Institution]:
        """Search institutions by name."""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Institution | None:
        """Get institution by exact name."""
        pass
