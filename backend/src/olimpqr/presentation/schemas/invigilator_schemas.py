"""Invigilator-related Pydantic schemas."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

from ...domain.value_objects import EventType


class RecordEventRequest(BaseModel):
    """Request to record a participant event."""
    attempt_id: UUID
    event_type: EventType
    timestamp: datetime | None = None


class RecordEventResponse(BaseModel):
    """Response after recording event."""
    id: UUID
    attempt_id: UUID
    event_type: str
    timestamp: datetime


class IssueExtraSheetRequest(BaseModel):
    """Request to issue an extra answer sheet."""
    attempt_id: UUID


class IssueExtraSheetResponse(BaseModel):
    """Response after issuing extra sheet."""
    answer_sheet_id: UUID
    sheet_token: str
    pdf_url: str


class EventItem(BaseModel):
    """Single event item."""
    id: UUID
    attempt_id: UUID
    event_type: str
    timestamp: datetime
    recorded_by: UUID


class AttemptEventsResponse(BaseModel):
    """Response with attempt events."""
    events: list[EventItem]
