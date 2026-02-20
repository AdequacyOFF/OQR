"""Participant event model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from olimpqr.domain.value_objects.event_type import EventType

from ..base import Base

if TYPE_CHECKING:
    from .attempt import AttemptModel
    from .user import UserModel


class ParticipantEventModel(Base):
    """Participant event database model."""

    __tablename__ = "participant_events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(
            EventType,
            name="eventtype",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [member.value for member in e],
        ),
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )
    recorded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    attempt: Mapped["AttemptModel"] = relationship(
        "AttemptModel",
        lazy="selectin"
    )
    recorder: Mapped["UserModel"] = relationship(
        "UserModel",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ParticipantEventModel(id={self.id}, attempt_id={self.attempt_id}, event_type={self.event_type})>"
