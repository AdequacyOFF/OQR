"""Audit log repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import AuditLog
from ...domain.repositories import AuditLogRepository
from ..database.models import AuditLogModel


class AuditLogRepositoryImpl(AuditLogRepository):
    """SQLAlchemy implementation of AuditLogRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        model = AuditLogModel(
            id=entity.id,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            action=entity.action,
            user_id=entity.user_id,
            ip_address=entity.ip_address,
            details=entity.details,
            timestamp=entity.timestamp
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> AuditLog | None:
        """Get audit log by ID."""
        result = await self.session.execute(
            select(AuditLogModel).where(AuditLogModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get all audit logs with pagination."""
        result = await self.session.execute(
            select(AuditLogModel)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogModel.timestamp.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, entity: AuditLog) -> AuditLog:
        """Update an audit log (generally not recommended - logs should be immutable)."""
        result = await self.session.execute(
            select(AuditLogModel).where(AuditLogModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Запись журнала с id {entity.id} не найдена")

        # Only allow updating details in case of correction
        model.details = entity.details

        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an audit log (generally not recommended - logs should be immutable)."""
        result = await self.session.execute(
            select(AuditLogModel).where(AuditLogModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_entity(
        self, entity_type: str, entity_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for a specific entity."""
        result = await self.session.execute(
            select(AuditLogModel)
            .where(
                AuditLogModel.entity_type == entity_type,
                AuditLogModel.entity_id == entity_id
            )
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogModel.timestamp.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs for a specific user."""
        result = await self.session.execute(
            select(AuditLogModel)
            .where(AuditLogModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(AuditLogModel.timestamp.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: AuditLogModel) -> AuditLog:
        """Convert SQLAlchemy model to domain entity."""
        return AuditLog(
            id=model.id,
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            action=model.action,
            user_id=model.user_id,
            ip_address=model.ip_address,
            details=model.details or {},
            timestamp=model.timestamp
        )
