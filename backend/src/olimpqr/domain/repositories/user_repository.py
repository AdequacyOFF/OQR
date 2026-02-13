"""User repository interface."""

from abc import abstractmethod
from typing import List

from .base import BaseRepository
from ..entities import User
from ..value_objects import UserRole


class UserRepository(BaseRepository[User]):
    """Repository interface for User entity."""

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User email

        Returns:
            User if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role.

        Args:
            role: User role to filter by
            skip: Number of users to skip
            limit: Maximum number of users to return

        Returns:
            List of users with the specified role
        """
        pass

    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """Check if user with email exists.

        Args:
            email: Email to check

        Returns:
            True if user exists, False otherwise
        """
        pass
