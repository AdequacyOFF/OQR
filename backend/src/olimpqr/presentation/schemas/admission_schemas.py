"""Admission-related Pydantic schemas."""

from pydantic import BaseModel, Field
from uuid import UUID


class VerifyEntryQRRequest(BaseModel):
    """Request to verify entry QR code."""
    token: str = Field(..., description="Raw token scanned from QR code")


class VerifyEntryQRResponse(BaseModel):
    """Response after verifying entry QR code."""
    registration_id: UUID
    participant_name: str
    participant_school: str
    participant_grade: int
    competition_name: str
    competition_id: UUID
    can_proceed: bool
    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "registration_id": "123e4567-e89b-12d3-a456-426614174000",
                "participant_name": "Иван Иванов",
                "participant_school": "Школа №1",
                "participant_grade": 10,
                "competition_name": "Олимпиада по математике",
                "competition_id": "123e4567-e89b-12d3-a456-426614174001",
                "can_proceed": True,
                "message": "Participant verified. Proceed with admission."
            }]
        }
    }


class ApproveAdmissionRequest(BaseModel):
    """Request to approve admission."""
    raw_entry_token: str = Field(..., description="Raw entry token for re-verification")


class ApproveAdmissionResponse(BaseModel):
    """Response after approving admission with answer sheet."""
    attempt_id: UUID
    variant_number: int
    pdf_url: str
    sheet_token: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "attempt_id": "123e4567-e89b-12d3-a456-426614174000",
                "variant_number": 2,
                "pdf_url": "http://minio:9000/answer-sheets/...",
                "sheet_token": "abc123..."
            }]
        }
    }
