"""Audit log repository interface."""

from abc import abstractmethod
from typing import List
from uuid import UUID

from .base import BaseRepository
from ..entities import AuditLog


class AuditLogRepository(BaseRepository[AuditLog]):
    """Repository interface for AuditLog entity."""

    @abstractmethod
    async def get_by_entity(
        self, entity_type: str, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a specific entity."""
        pass

    @abstractmethod
    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        pass
