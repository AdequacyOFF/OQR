"""User model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from olimpqr.domain.value_objects.user_role import UserRole

from ..base import Base

if TYPE_CHECKING:
    from .audit_log import AuditLogModel
    from .competition import CompetitionModel
    from .participant import ParticipantModel
    from .scan import ScanModel


class UserModel(Base):
    """User database model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="userrole",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [member.value for member in e],
        ),
        nullable=False,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    participant: Mapped["ParticipantModel"] = relationship(
        "ParticipantModel",
        back_populates="user",
        uselist=False,
        lazy="selectin"
    )
    competitions_created: Mapped[list["CompetitionModel"]] = relationship(
        "CompetitionModel",
        back_populates="creator",
        foreign_keys="CompetitionModel.created_by"
    )
    scans_uploaded: Mapped[list["ScanModel"]] = relationship(
        "ScanModel",
        back_populates="uploader",
        foreign_keys="ScanModel.uploaded_by"
    )
    scans_verified: Mapped[list["ScanModel"]] = relationship(
        "ScanModel",
        back_populates="verifier",
        foreign_keys="ScanModel.verified_by"
    )
    audit_logs: Mapped[list["AuditLogModel"]] = relationship(
        "AuditLogModel",
        back_populates="user"
    )

    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role})>"
