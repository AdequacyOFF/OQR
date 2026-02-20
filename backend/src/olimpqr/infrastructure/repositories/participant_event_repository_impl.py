"""Participant event repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import ParticipantEvent
from ...domain.repositories import ParticipantEventRepository
from ...domain.value_objects import EventType
from ..database.models import ParticipantEventModel


class ParticipantEventRepositoryImpl(ParticipantEventRepository):
    """SQLAlchemy implementation of ParticipantEventRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: ParticipantEvent) -> ParticipantEvent:
        model = ParticipantEventModel(
            id=entity.id,
            attempt_id=entity.attempt_id,
            event_type=entity.event_type,
            timestamp=entity.timestamp,
            recorded_by=entity.recorded_by,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> ParticipantEvent | None:
        result = await self.session.execute(
            select(ParticipantEventModel).where(ParticipantEventModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ParticipantEvent]:
        result = await self.session.execute(
            select(ParticipantEventModel).offset(skip).limit(limit)
            .order_by(ParticipantEventModel.timestamp.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: ParticipantEvent) -> ParticipantEvent:
        result = await self.session.execute(
            select(ParticipantEventModel).where(ParticipantEventModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Событие с id {entity.id} не найдено")
        model.event_type = entity.event_type
        model.timestamp = entity.timestamp
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(ParticipantEventModel).where(ParticipantEventModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_attempt(self, attempt_id: UUID) -> List[ParticipantEvent]:
        result = await self.session.execute(
            select(ParticipantEventModel)
            .where(ParticipantEventModel.attempt_id == attempt_id)
            .order_by(ParticipantEventModel.timestamp)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: ParticipantEventModel) -> ParticipantEvent:
        return ParticipantEvent(
            id=model.id,
            attempt_id=model.attempt_id,
            event_type=EventType(model.event_type) if isinstance(model.event_type, str) else model.event_type,
            timestamp=model.timestamp,
            recorded_by=model.recorded_by,
            created_at=model.created_at,
        )
