"""Room entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Room:
    """Room entity - competition room for seating participants.

    Attributes:
        id: Unique identifier
        competition_id: Reference to Competition
        name: Room name/number
        capacity: Maximum number of seats
        created_at: When room was created
    """
    competition_id: UUID
    name: str
    capacity: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 1:
            raise ValueError("Название аудитории не может быть пустым")
        if self.capacity < 1:
            raise ValueError("Вместимость аудитории должна быть положительной")
