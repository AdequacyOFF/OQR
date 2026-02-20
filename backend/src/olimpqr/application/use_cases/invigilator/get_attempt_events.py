"""Get attempt events use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ....domain.repositories import ParticipantEventRepository


@dataclass
class EventItem:
    id: UUID
    attempt_id: UUID
    event_type: str
    timestamp: datetime
    recorded_by: UUID


class GetAttemptEventsUseCase:
    """Get all events for an attempt."""

    def __init__(self, event_repository: ParticipantEventRepository):
        self.event_repo = event_repository

    async def execute(self, attempt_id: UUID) -> list[EventItem]:
        events = await self.event_repo.get_by_attempt(attempt_id)
        return [
            EventItem(
                id=e.id,
                attempt_id=e.attempt_id,
                event_type=e.event_type.value,
                timestamp=e.timestamp,
                recorded_by=e.recorded_by,
            )
            for e in events
        ]
