"""Seat assignment repository implementation."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import SeatAssignment
from ...domain.repositories import SeatAssignmentRepository
from ..database.models import SeatAssignmentModel, RegistrationModel, ParticipantModel


class SeatAssignmentRepositoryImpl(SeatAssignmentRepository):
    """SQLAlchemy implementation of SeatAssignmentRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: SeatAssignment) -> SeatAssignment:
        model = SeatAssignmentModel(
            id=entity.id,
            registration_id=entity.registration_id,
            room_id=entity.room_id,
            seat_number=entity.seat_number,
            variant_number=entity.variant_number,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> SeatAssignment | None:
        result = await self.session.execute(
            select(SeatAssignmentModel).where(SeatAssignmentModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[SeatAssignment]:
        result = await self.session.execute(
            select(SeatAssignmentModel).offset(skip).limit(limit)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: SeatAssignment) -> SeatAssignment:
        result = await self.session.execute(
            select(SeatAssignmentModel).where(SeatAssignmentModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Назначение места с id {entity.id} не найдено")
        model.room_id = entity.room_id
        model.seat_number = entity.seat_number
        model.variant_number = entity.variant_number
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(SeatAssignmentModel).where(SeatAssignmentModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_registration(self, registration_id: UUID) -> SeatAssignment | None:
        result = await self.session.execute(
            select(SeatAssignmentModel)
            .where(SeatAssignmentModel.registration_id == registration_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_room(self, room_id: UUID) -> List[SeatAssignment]:
        result = await self.session.execute(
            select(SeatAssignmentModel)
            .where(SeatAssignmentModel.room_id == room_id)
            .order_by(SeatAssignmentModel.seat_number)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def count_by_room(self, room_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(SeatAssignmentModel.id))
            .where(SeatAssignmentModel.room_id == room_id)
        )
        return result.scalar_one()

    async def count_by_room_and_institution(self, room_id: UUID, institution_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(SeatAssignmentModel.id))
            .join(RegistrationModel, SeatAssignmentModel.registration_id == RegistrationModel.id)
            .join(ParticipantModel, RegistrationModel.participant_id == ParticipantModel.id)
            .where(
                SeatAssignmentModel.room_id == room_id,
                ParticipantModel.institution_id == institution_id,
            )
        )
        return result.scalar_one()

    def _to_entity(self, model: SeatAssignmentModel) -> SeatAssignment:
        return SeatAssignment(
            id=model.id,
            registration_id=model.registration_id,
            room_id=model.room_id,
            seat_number=model.seat_number,
            variant_number=model.variant_number,
            created_at=model.created_at,
        )
