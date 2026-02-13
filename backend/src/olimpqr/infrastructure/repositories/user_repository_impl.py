"""User repository implementation."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from ...domain.entities import User
from ...domain.repositories import UserRepository
from ...domain.value_objects import UserRole
from ..database.models import UserModel


class UserRepositoryImpl(UserRepository):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: User) -> User:
        """Create a new user."""
        model = UserModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        self.session.add(model)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        result = await self.session.execute(
            select(UserModel)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, entity: User) -> User:
        """Update an existing user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == entity.id)
        )
        model = result.scalar_one_or_none()
        if not model:
            raise ValueError(f"User with id {entity.id} not found")

        model.email = entity.email
        model.password_hash = entity.password_hash
        model.role = entity.role
        model.is_active = entity.is_active
        model.updated_at = entity.updated_at

        await self.session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Delete a user."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == entity_id)
        )
        model = result.scalar_one_or_none()
        if not model:
            return False

        await self.session.delete(model)
        await self.session.flush()
        return True

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.role == role)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists."""
        result = await self.session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    def _to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
