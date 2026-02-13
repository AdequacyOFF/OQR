"""Attempt repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Attempt


class AttemptRepository(BaseRepository[Attempt]):
    """Repository interface for Attempt entity."""

    @abstractmethod
    async def get_by_sheet_token_hash(self, sheet_token_hash: str) -> Attempt | None:
        """Get attempt by sheet token hash."""
        pass

    @abstractmethod
    async def get_by_registration(self, registration_id: UUID) -> Attempt | None:
        """Get attempt by registration ID."""
        pass

    @abstractmethod
    async def get_by_competition(self, competition_id: UUID, skip: int = 0, limit: int = 1000) -> List[Attempt]:
        """Get all attempts for a competition."""
        pass
