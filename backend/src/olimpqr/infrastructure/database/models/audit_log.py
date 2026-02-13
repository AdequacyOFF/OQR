"""Audit log model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .user import UserModel


class AuditLogModel(Base):
    """Audit log database model."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity_type_id", "entity_type", "entity_id"),
        Index("ix_audit_logs_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_logs_action_timestamp", "action", "timestamp"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True
    )
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    # Relationships
    user: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="audit_logs",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AuditLogModel(id={self.id}, entity_type={self.entity_type}, action={self.action}, timestamp={self.timestamp})>"
