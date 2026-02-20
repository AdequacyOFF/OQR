"""Document repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import Document


class DocumentRepository(BaseRepository[Document]):
    """Repository interface for Document entity."""

    @abstractmethod
    async def get_by_participant(self, participant_id: UUID) -> List[Document]:
        """Get all documents for a participant."""
        pass
