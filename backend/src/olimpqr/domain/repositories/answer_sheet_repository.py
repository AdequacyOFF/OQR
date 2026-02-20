"""Answer sheet repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import AnswerSheet


class AnswerSheetRepository(BaseRepository[AnswerSheet]):
    """Repository interface for AnswerSheet entity."""

    @abstractmethod
    async def get_by_attempt(self, attempt_id: UUID) -> List[AnswerSheet]:
        """Get all answer sheets for an attempt."""
        pass

    @abstractmethod
    async def get_by_token_hash(self, token_hash: str) -> AnswerSheet | None:
        """Get answer sheet by token hash."""
        pass

    @abstractmethod
    async def get_primary_by_attempt(self, attempt_id: UUID) -> AnswerSheet | None:
        """Get the primary answer sheet for an attempt."""
        pass
