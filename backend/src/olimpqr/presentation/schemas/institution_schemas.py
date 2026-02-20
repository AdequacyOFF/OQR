"""Institution-related Pydantic schemas."""

from pydantic import BaseModel, Field
from uuid import UUID


class CreateInstitutionRequest(BaseModel):
    """Request to create an institution."""
    name: str = Field(..., min_length=2, max_length=255)
    short_name: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=255)


class UpdateInstitutionRequest(BaseModel):
    """Request to update an institution."""
    name: str = Field(..., min_length=2, max_length=255)
    short_name: str | None = Field(None, max_length=100)
    city: str | None = Field(None, max_length=255)


class InstitutionResponse(BaseModel):
    """Institution response."""
    id: UUID
    name: str
    short_name: str | None = None
    city: str | None = None


class InstitutionListResponse(BaseModel):
    """List of institutions."""
    institutions: list[InstitutionResponse]
    total: int
