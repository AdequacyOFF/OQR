"""Registration-related Pydantic schemas."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

from ...domain.value_objects import RegistrationStatus


class RegisterForCompetitionRequest(BaseModel):
    """Request to register for competition."""
    competition_id: UUID


class RegistrationResponse(BaseModel):
    """Response with registration info."""
    id: UUID
    participant_id: UUID
    competition_id: UUID
    status: RegistrationStatus
    created_at: datetime
    entry_token: str | None = None  # Only included on creation

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "participant_id": "123e4567-e89b-12d3-a456-426614174001",
                "competition_id": "123e4567-e89b-12d3-a456-426614174002",
                "status": "pending",
                "created_at": "2026-02-12T12:00:00",
                "entry_token": "abcdef123456..."
            }]
        }
    }


class RegistrationListResponse(BaseModel):
    """Response with list of registrations."""
    items: list[RegistrationResponse]
    total: int


class EntryQRResponse(BaseModel):
    """Response with entry QR code."""
    qr_code_base64: str
    registration_id: UUID
    expires_at: datetime
    is_used: bool

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "qr_code_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
                "registration_id": "123e4567-e89b-12d3-a456-426614174000",
                "expires_at": "2026-02-13T12:00:00",
                "is_used": False
            }]
        }
    }
