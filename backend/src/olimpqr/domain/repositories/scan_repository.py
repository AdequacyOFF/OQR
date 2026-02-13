"""Scan repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Scan


class ScanRepository(BaseRepository[Scan]):
    """Repository interface for Scan entity."""

    @abstractmethod
    async def get_by_attempt(self, attempt_id: UUID) -> List[Scan]:
        """Get all scans for an attempt."""
        pass

    @abstractmethod
    async def get_unverified(self, skip: int = 0, limit: int = 100) -> List[Scan]:
        """Get scans that haven't been manually verified."""
        pass
