"""Record participant event use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ....domain.entities import ParticipantEvent
from ....domain.value_objects import EventType
from ....domain.repositories import ParticipantEventRepository, AttemptRepository


@dataclass
class RecordEventResult:
    id: UUID
    attempt_id: UUID
    event_type: str
    timestamp: datetime


class RecordEventUseCase:
    """Record a participant event during competition (by invigilator)."""

    def __init__(
        self,
        event_repository: ParticipantEventRepository,
        attempt_repository: AttemptRepository,
    ):
        self.event_repo = event_repository
        self.attempt_repo = attempt_repository

    async def execute(
        self,
        attempt_id: UUID,
        event_type: EventType,
        recorded_by: UUID,
        timestamp: datetime | None = None,
    ) -> RecordEventResult:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise ValueError("Попытка не найдена")

        event = ParticipantEvent(
            attempt_id=attempt_id,
            event_type=event_type,
            recorded_by=recorded_by,
            timestamp=timestamp or datetime.utcnow(),
        )
        await self.event_repo.create(event)

        return RecordEventResult(
            id=event.id,
            attempt_id=event.attempt_id,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
        )
