"""Institution repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import Institution
from ...domain.repositories import InstitutionRepository
from ..database.models import InstitutionModel


class InstitutionRepositoryImpl(InstitutionRepository):
    """SQLAlchemy implementation of InstitutionRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Institution) -> Institution:
        model = InstitutionModel(
            id=entity.id,
            name=entity.name,
            short_name=entity.short_name,
            city=entity.city,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> Institution | None:
        result = await self.session.execute(
            select(InstitutionModel).where(InstitutionModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Institution]:
        result = await self.session.execute(
            select(InstitutionModel)
            .offset(skip).limit(limit)
            .order_by(InstitutionModel.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: Institution) -> Institution:
        result = await self.session.execute(
            select(InstitutionModel).where(InstitutionModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Учреждение с id {entity.id} не найдено")
        model.name = entity.name
        model.short_name = entity.short_name
        model.city = entity.city
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(InstitutionModel).where(InstitutionModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def search(self, query: str, limit: int = 20) -> List[Institution]:
        result = await self.session.execute(
            select(InstitutionModel)
            .where(InstitutionModel.name.ilike(f"%{query}%"))
            .limit(limit)
            .order_by(InstitutionModel.name)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_name(self, name: str) -> Institution | None:
        result = await self.session.execute(
            select(InstitutionModel).where(InstitutionModel.name == name)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: InstitutionModel) -> Institution:
        return Institution(
            id=model.id,
            name=model.name,
            short_name=model.short_name,
            city=model.city,
            created_at=model.created_at,
        )
