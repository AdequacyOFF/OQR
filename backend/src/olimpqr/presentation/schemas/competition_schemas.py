"""Competition-related Pydantic schemas."""

from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field
from uuid import UUID

from ...domain.value_objects import CompetitionStatus
from ...domain.entities import Competition


class CreateCompetitionRequest(BaseModel):
    """Request schema for creating a competition."""
    name: str = Field(..., min_length=3, description="Competition name")
    date: date = Field(..., description="Competition date")
    registration_start: datetime = Field(..., description="Registration start datetime")
    registration_end: datetime = Field(..., description="Registration end datetime")
    variants_count: int = Field(..., ge=1, description="Number of test variants")
    max_score: int = Field(..., ge=1, description="Maximum possible score")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Математическая олимпиада 2026",
                    "date": "2026-03-15",
                    "registration_start": "2026-02-01T00:00:00",
                    "registration_end": "2026-03-10T23:59:59",
                    "variants_count": 4,
                    "max_score": 100
                }
            ]
        }
    }


class UpdateCompetitionRequest(BaseModel):
    """Request schema for updating a competition. All fields are optional."""
    name: str | None = Field(None, min_length=3, description="Competition name")
    date: date | None = Field(None, description="Competition date")
    registration_start: datetime | None = Field(None, description="Registration start datetime")
    registration_end: datetime | None = Field(None, description="Registration end datetime")
    variants_count: int | None = Field(None, ge=1, description="Number of test variants")
    max_score: int | None = Field(None, ge=1, description="Maximum possible score")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Математическая олимпиада 2026 (обновлено)",
                    "max_score": 120
                }
            ]
        }
    }


class CompetitionResponse(BaseModel):
    """Response schema for competition data."""
    id: UUID
    name: str
    date: date
    registration_start: datetime
    registration_end: datetime
    variants_count: int
    max_score: int
    status: CompetitionStatus
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: Competition) -> "CompetitionResponse":
        """Create response from Competition entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            date=entity.date,
            registration_start=entity.registration_start,
            registration_end=entity.registration_end,
            variants_count=entity.variants_count,
            max_score=entity.max_score,
            status=entity.status,
            created_by=entity.created_by,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Математическая олимпиада 2026",
                    "date": "2026-03-15",
                    "registration_start": "2026-02-01T00:00:00",
                    "registration_end": "2026-03-10T23:59:59",
                    "variants_count": 4,
                    "max_score": 100,
                    "status": "draft",
                    "created_by": "123e4567-e89b-12d3-a456-426614174001",
                    "created_at": "2026-02-01T10:00:00",
                    "updated_at": "2026-02-01T10:00:00"
                }
            ]
        }
    }


class CompetitionListResponse(BaseModel):
    """Response schema for list of competitions."""
    competitions: List[CompetitionResponse]
    total: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "competitions": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Математическая олимпиада 2026",
                            "date": "2026-03-15",
                            "registration_start": "2026-02-01T00:00:00",
                            "registration_end": "2026-03-10T23:59:59",
                            "variants_count": 4,
                            "max_score": 100,
                            "status": "registration_open",
                            "created_by": "123e4567-e89b-12d3-a456-426614174001",
                            "created_at": "2026-02-01T10:00:00",
                            "updated_at": "2026-02-05T10:00:00"
                        }
                    ],
                    "total": 1
                }
            ]
        }
    }
