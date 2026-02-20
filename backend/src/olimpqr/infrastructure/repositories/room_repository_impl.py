"""Room repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import Room
from ...domain.repositories import RoomRepository
from ..database.models import RoomModel


class RoomRepositoryImpl(RoomRepository):
    """SQLAlchemy implementation of RoomRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Room) -> Room:
        model = RoomModel(
            id=entity.id,
            competition_id=entity.competition_id,
            name=entity.name,
            capacity=entity.capacity,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> Room | None:
        result = await self.session.execute(
            select(RoomModel).where(RoomModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Room]:
        result = await self.session.execute(
            select(RoomModel).offset(skip).limit(limit).order_by(RoomModel.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: Room) -> Room:
        result = await self.session.execute(
            select(RoomModel).where(RoomModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Аудитория с id {entity.id} не найдена")
        model.name = entity.name
        model.capacity = entity.capacity
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(RoomModel).where(RoomModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_competition(self, competition_id: UUID) -> List[Room]:
        result = await self.session.execute(
            select(RoomModel)
            .where(RoomModel.competition_id == competition_id)
            .order_by(RoomModel.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: RoomModel) -> Room:
        return Room(
            id=model.id,
            competition_id=model.competition_id,
            name=model.name,
            capacity=model.capacity,
            created_at=model.created_at,
        )
