"""Base repository interface."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from uuid import UUID

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Base repository interface for CRUD operations."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity.

        Args:
            entity: Entity to create

        Returns:
            Created entity with generated ID
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> T | None:
        """Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Entity if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination.

        Args:
            skip: Number of entities to skip
            limit: Maximum number of entities to return

        Returns:
            List of entities
        """
        pass

    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update an existing entity.

        Args:
            entity: Entity with updated values

        Returns:
            Updated entity
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: UUID) -> bool:
        """Delete an entity.

        Args:
            entity_id: Entity ID

        Returns:
            True if deleted, False if not found
        """
        pass
