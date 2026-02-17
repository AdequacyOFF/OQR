"""Profile-related Pydantic schemas."""

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class ParticipantProfileResponse(BaseModel):
    """Response with participant profile info."""
    id: UUID
    user_id: UUID
    full_name: str
    school: str
    grade: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "123e4567-e89b-12d3-a456-426614174001",
                "full_name": "Иванов Иван Иванович",
                "school": "Школа №1",
                "grade": 10,
                "created_at": "2026-02-12T12:00:00",
                "updated_at": "2026-02-13T14:30:00"
            }]
        }
    }


class UpdateProfileRequest(BaseModel):
    """Request to update participant profile."""
    full_name: str = Field(min_length=2, description="ФИО (минимум 2 символа)")
    school: str = Field(min_length=2, description="Название школы (минимум 2 символа)")
    grade: int = Field(ge=1, le=12, description="Класс (1-12)")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "full_name": "Иванов Иван Иванович",
                "school": "Школа №1",
                "grade": 10
            }]
        }
    }
