"""Registration repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import Registration
from ...domain.repositories import RegistrationRepository
from ..database.models import RegistrationModel


class RegistrationRepositoryImpl(RegistrationRepository):
    """SQLAlchemy implementation of RegistrationRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Registration) -> Registration:
        """Create a new registration."""
        model = RegistrationModel(
            id=entity.id,
            participant_id=entity.participant_id,
            competition_id=entity.competition_id,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> Registration | None:
        """Get registration by ID."""
        result = await self.session.execute(
            select(RegistrationModel).where(RegistrationModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Registration]:
        """Get all registrations with pagination."""
        result = await self.session.execute(
            select(RegistrationModel)
            .offset(skip)
            .limit(limit)
            .order_by(RegistrationModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, entity: Registration) -> Registration:
        """Update an existing registration."""
        result = await self.session.execute(
            select(RegistrationModel).where(RegistrationModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Registration with id {entity.id} not found")

        model.status = entity.status
        model.updated_at = entity.updated_at

        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete a registration."""
        result = await self.session.execute(
            select(RegistrationModel).where(RegistrationModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_participant_and_competition(
        self, participant_id: UUID, competition_id: UUID
    ) -> Registration | None:
        """Get registration by participant and competition."""
        result = await self.session.execute(
            select(RegistrationModel).where(
                RegistrationModel.participant_id == participant_id,
                RegistrationModel.competition_id == competition_id
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_competition(
        self, competition_id: UUID, skip: int = 0, limit: int = 1000
    ) -> List[Registration]:
        """Get all registrations for a competition."""
        result = await self.session.execute(
            select(RegistrationModel)
            .where(RegistrationModel.competition_id == competition_id)
            .offset(skip)
            .limit(limit)
            .order_by(RegistrationModel.created_at.asc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_by_participant_id(
        self, participant_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Registration]:
        """Get all registrations for a participant."""
        result = await self.session.execute(
            select(RegistrationModel)
            .where(RegistrationModel.participant_id == participant_id)
            .offset(skip)
            .limit(limit)
            .order_by(RegistrationModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    def _to_entity(self, model: RegistrationModel) -> Registration:
        """Convert SQLAlchemy model to domain entity."""
        return Registration(
            id=model.id,
            participant_id=model.participant_id,
            competition_id=model.competition_id,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
