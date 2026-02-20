"""Seat assignment entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class SeatAssignment:
    """Seat assignment entity - assigns a participant to a room and seat.

    Attributes:
        id: Unique identifier
        registration_id: Reference to Registration (unique - one seat per registration)
        room_id: Reference to Room
        seat_number: Seat number within the room
        variant_number: Assigned variant number
        created_at: When assignment was created
    """
    registration_id: UUID
    room_id: UUID
    seat_number: int
    variant_number: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.seat_number < 1:
            raise ValueError("Номер места должен быть положительным")
        if self.variant_number < 1:
            raise ValueError("Номер варианта должен быть положительным")
