"""Room model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .competition import CompetitionModel
    from .seat_assignment import SeatAssignmentModel


class RoomModel(Base):
    """Room database model."""

    __tablename__ = "rooms"
    __table_args__ = (
        UniqueConstraint("competition_id", "name", name="uq_room_competition_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    competition_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("competitions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    competition: Mapped["CompetitionModel"] = relationship(
        "CompetitionModel",
        lazy="selectin"
    )
    seat_assignments: Mapped[list["SeatAssignmentModel"]] = relationship(
        "SeatAssignmentModel",
        back_populates="room"
    )

    def __repr__(self) -> str:
        return f"<RoomModel(id={self.id}, name={self.name}, capacity={self.capacity})>"
