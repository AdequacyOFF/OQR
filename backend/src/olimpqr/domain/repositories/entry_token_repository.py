"""Entry token repository interface."""

from abc import abstractmethod
from uuid import UUID

from .base import BaseRepository
from ..entities import EntryToken


class EntryTokenRepository(BaseRepository[EntryToken]):
    """Repository interface for EntryToken entity."""

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> EntryToken | None:
        """Get entry token by token hash."""
        pass

    @abstractmethod
    async def get_by_registration(self, registration_id: UUID) -> EntryToken | None:
        """Get entry token by registration ID."""
        pass
