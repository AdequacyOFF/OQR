"""Participant event entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects import EventType


@dataclass
class ParticipantEvent:
    """Participant event entity - records events during competition.

    Attributes:
        id: Unique identifier
        attempt_id: Reference to Attempt
        event_type: Type of event
        timestamp: When the event occurred
        recorded_by: User who recorded the event (invigilator)
        created_at: When record was created
    """
    attempt_id: UUID
    event_type: EventType
    recorded_by: UUID
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.event_type, EventType):
            raise TypeError("event_type must be an EventType instance")
