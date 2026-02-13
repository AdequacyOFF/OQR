"""Participant model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .registration import RegistrationModel
    from .user import UserModel


class ParticipantModel(Base):
    """Participant database model."""

    __tablename__ = "participants"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    school: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    grade: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
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
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="participant",
        lazy="selectin"
    )
    registrations: Mapped[list["RegistrationModel"]] = relationship(
        "RegistrationModel",
        back_populates="participant"
    )

    def __repr__(self) -> str:
        return f"<ParticipantModel(id={self.id}, full_name={self.full_name}, grade={self.grade})>"
