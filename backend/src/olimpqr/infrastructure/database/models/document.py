"""Document model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .participant import ParticipantModel


class DocumentModel(Base):
    """Document database model."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    participant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("participants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    participant: Mapped["ParticipantModel"] = relationship(
        "ParticipantModel",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<DocumentModel(id={self.id}, participant_id={self.participant_id}, file_type={self.file_type})>"
