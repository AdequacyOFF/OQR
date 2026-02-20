"""Answer sheet repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import AnswerSheet
from ...domain.repositories import AnswerSheetRepository
from ...domain.value_objects import SheetKind
from ...domain.value_objects.token import TokenHash
from ..database.models import AnswerSheetModel


class AnswerSheetRepositoryImpl(AnswerSheetRepository):
    """SQLAlchemy implementation of AnswerSheetRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: AnswerSheet) -> AnswerSheet:
        model = AnswerSheetModel(
            id=entity.id,
            attempt_id=entity.attempt_id,
            sheet_token_hash=entity.sheet_token_hash.value,
            kind=entity.kind,
            pdf_file_path=entity.pdf_file_path,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> AnswerSheet | None:
        result = await self.session.execute(
            select(AnswerSheetModel).where(AnswerSheetModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AnswerSheet]:
        result = await self.session.execute(
            select(AnswerSheetModel).offset(skip).limit(limit)
            .order_by(AnswerSheetModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: AnswerSheet) -> AnswerSheet:
        result = await self.session.execute(
            select(AnswerSheetModel).where(AnswerSheetModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Бланк ответов с id {entity.id} не найден")
        model.pdf_file_path = entity.pdf_file_path
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(AnswerSheetModel).where(AnswerSheetModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_attempt(self, attempt_id: UUID) -> List[AnswerSheet]:
        result = await self.session.execute(
            select(AnswerSheetModel)
            .where(AnswerSheetModel.attempt_id == attempt_id)
            .order_by(AnswerSheetModel.created_at)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_by_token_hash(self, token_hash: str) -> AnswerSheet | None:
        result = await self.session.execute(
            select(AnswerSheetModel)
            .where(AnswerSheetModel.sheet_token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_primary_by_attempt(self, attempt_id: UUID) -> AnswerSheet | None:
        result = await self.session.execute(
            select(AnswerSheetModel)
            .where(
                AnswerSheetModel.attempt_id == attempt_id,
                AnswerSheetModel.kind == SheetKind.PRIMARY,
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: AnswerSheetModel) -> AnswerSheet:
        return AnswerSheet(
            id=model.id,
            attempt_id=model.attempt_id,
            sheet_token_hash=TokenHash(value=model.sheet_token_hash),
            kind=SheetKind(model.kind) if isinstance(model.kind, str) else model.kind,
            pdf_file_path=model.pdf_file_path,
            created_at=model.created_at,
        )
