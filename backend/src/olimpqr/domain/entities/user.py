"""User entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects import UserRole


@dataclass
class User:
    """User entity representing system users (all roles).

    Attributes:
        id: Unique identifier
        email: User email (unique, used for login)
        password_hash: Bcrypt hashed password
        role: User role (participant, admitter, scanner, admin)
        is_active: Whether user account is active
        created_at: When user was created
        updated_at: When user was last updated
    """
    email: str
    password_hash: str
    role: UserRole
    id: UUID = field(default_factory=uuid4)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.email or "@" not in self.email:
            raise ValueError("Некорректный email адрес")
        if not self.password_hash:
            raise ValueError("Хеш пароля не может быть пустым")
        if not isinstance(self.role, UserRole):
            raise TypeError("Role must be a UserRole instance")

    def deactivate(self):
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate user account."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def change_role(self, new_role: UserRole):
        """Change user role."""
        if not isinstance(new_role, UserRole):
            raise TypeError("Role must be a UserRole instance")
        self.role = new_role
        self.updated_at = datetime.utcnow()
