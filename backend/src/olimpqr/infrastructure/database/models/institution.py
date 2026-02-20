"""Institution model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .participant import ParticipantModel


class InstitutionModel(Base):
    """Institution database model."""

    __tablename__ = "institutions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True
    )
    short_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    city: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    participants: Mapped[list["ParticipantModel"]] = relationship(
        "ParticipantModel",
        back_populates="institution"
    )

    def __repr__(self) -> str:
        return f"<InstitutionModel(id={self.id}, name={self.name})>"
