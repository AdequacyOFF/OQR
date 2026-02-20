"""Event type enumeration for participant events."""

from enum import Enum


class EventType(str, Enum):
    """Types of events that can be recorded for a participant during competition."""
    START_WORK = "start_work"
    SUBMIT = "submit"
    EXIT_ROOM = "exit_room"
    ENTER_ROOM = "enter_room"
