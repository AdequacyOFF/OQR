"""Seat assignment model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .registration import RegistrationModel
    from .room import RoomModel


class SeatAssignmentModel(Base):
    """Seat assignment database model."""

    __tablename__ = "seat_assignments"
    __table_args__ = (
        UniqueConstraint("room_id", "seat_number", name="uq_room_seat"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    registration_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("registrations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    room_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    seat_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    variant_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    registration: Mapped["RegistrationModel"] = relationship(
        "RegistrationModel",
        lazy="selectin"
    )
    room: Mapped["RoomModel"] = relationship(
        "RoomModel",
        back_populates="seat_assignments",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<SeatAssignmentModel(id={self.id}, room_id={self.room_id}, seat={self.seat_number})>"
