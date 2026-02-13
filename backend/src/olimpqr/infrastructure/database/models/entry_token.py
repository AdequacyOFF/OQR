"""Entry token model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .registration import RegistrationModel


class EntryTokenModel(Base):
    """Entry token database model."""

    __tablename__ = "entry_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    registration_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    registration: Mapped["RegistrationModel"] = relationship(
        "RegistrationModel",
        back_populates="entry_token",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<EntryTokenModel(id={self.id}, registration_id={self.registration_id}, used_at={self.used_at})>"
