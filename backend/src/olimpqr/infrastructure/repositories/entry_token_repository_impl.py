"""Entry token repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import EntryToken
from ...domain.repositories import EntryTokenRepository
from ...domain.value_objects import TokenHash
from ..database.models import EntryTokenModel


class EntryTokenRepositoryImpl(EntryTokenRepository):
    """SQLAlchemy implementation of EntryTokenRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: EntryToken) -> EntryToken:
        """Create a new entry token."""
        model = EntryTokenModel(
            id=entity.id,
            token_hash=entity.token_hash.value,
            raw_token=entity.raw_token,
            registration_id=entity.registration_id,
            expires_at=entity.expires_at,
            used_at=entity.used_at,
            created_at=entity.created_at
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> EntryToken | None:
        """Get entry token by ID."""
        result = await self.session.execute(
            select(EntryTokenModel).where(EntryTokenModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[EntryToken]:
        """Get all entry tokens with pagination."""
        result = await self.session.execute(
            select(EntryTokenModel)
            .offset(skip)
            .limit(limit)
            .order_by(EntryTokenModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, entity: EntryToken) -> EntryToken:
        """Update an existing entry token."""
        result = await self.session.execute(
            select(EntryTokenModel).where(EntryTokenModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"EntryToken with id {entity.id} not found")

        model.expires_at = entity.expires_at
        model.used_at = entity.used_at

        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entry token."""
        result = await self.session.execute(
            select(EntryTokenModel).where(EntryTokenModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_token_hash(self, token_hash: str) -> EntryToken | None:
        """Get entry token by token hash."""
        result = await self.session.execute(
            select(EntryTokenModel).where(EntryTokenModel.token_hash == token_hash)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_registration(self, registration_id: UUID) -> EntryToken | None:
        """Get entry token by registration ID."""
        result = await self.session.execute(
            select(EntryTokenModel).where(EntryTokenModel.registration_id == registration_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: EntryTokenModel) -> EntryToken:
        """Convert SQLAlchemy model to domain entity."""
        return EntryToken(
            id=model.id,
            token_hash=TokenHash(value=model.token_hash),
            raw_token=model.raw_token,
            registration_id=model.registration_id,
            expires_at=model.expires_at,
            used_at=model.used_at,
            created_at=model.created_at
        )
