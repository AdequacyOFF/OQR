"""Document-related Pydantic schemas."""

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class DocumentResponse(BaseModel):
    """Document response."""
    id: UUID
    file_path: str
    file_type: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    """List of documents."""
    documents: list[DocumentResponse]
