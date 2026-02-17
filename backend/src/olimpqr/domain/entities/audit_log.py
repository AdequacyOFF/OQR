"""Audit log entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass
class AuditLog:
    """Audit log entity - tracks all important system actions.

    Attributes:
        id: Unique identifier
        entity_type: Type of entity being modified (e.g., "user", "attempt")
        entity_id: ID of the entity being modified
        action: Action performed (e.g., "created", "updated", "deleted")
        user_id: User who performed the action (None for system actions)
        ip_address: IP address of the request
        details: Additional details as JSON (before/after values, etc.)
        timestamp: When the action occurred
    """
    entity_type: str
    entity_id: UUID
    action: str
    id: UUID = field(default_factory=uuid4)
    user_id: UUID | None = None
    ip_address: str | None = None
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.entity_type:
            raise ValueError("Тип сущности не может быть пустым")
        if not self.action:
            raise ValueError("Действие не может быть пустым")

    @classmethod
    def create_log(
        cls,
        entity_type: str,
        entity_id: UUID,
        action: str,
        user_id: UUID | None = None,
        ip_address: str | None = None,
        **details: Any
    ) -> "AuditLog":
        """Create an audit log entry.

        Args:
            entity_type: Type of entity (e.g., "registration")
            entity_id: ID of the entity
            action: Action performed (e.g., "admitted", "score_applied")
            user_id: User who performed the action
            ip_address: IP address of the request
            **details: Additional context (before/after values, etc.)

        Returns:
            New AuditLog instance
        """
        return cls(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
