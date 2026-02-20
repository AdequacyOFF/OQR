"""Document repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import Document
from ...domain.repositories import DocumentRepository
from ..database.models import DocumentModel


class DocumentRepositoryImpl(DocumentRepository):
    """SQLAlchemy implementation of DocumentRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: Document) -> Document:
        model = DocumentModel(
            id=entity.id,
            participant_id=entity.participant_id,
            file_path=entity.file_path,
            file_type=entity.file_type,
            created_at=entity.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> Document | None:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Document]:
        result = await self.session.execute(
            select(DocumentModel).offset(skip).limit(limit)
            .order_by(DocumentModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, entity: Document) -> Document:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"Документ с id {entity.id} не найден")
        model.file_path = entity.file_path
        model.file_type = entity.file_type
        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        result = await self.session.execute(
            select(DocumentModel).where(DocumentModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_participant(self, participant_id: UUID) -> List[Document]:
        result = await self.session.execute(
            select(DocumentModel)
            .where(DocumentModel.participant_id == participant_id)
            .order_by(DocumentModel.created_at.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            participant_id=model.participant_id,
            file_path=model.file_path,
            file_type=model.file_type,
            created_at=model.created_at,
        )
