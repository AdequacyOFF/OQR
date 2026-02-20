"""Room-related Pydantic schemas."""

from pydantic import BaseModel, Field
from uuid import UUID


class CreateRoomRequest(BaseModel):
    """Request to create a room."""
    name: str = Field(..., min_length=1, max_length=100)
    capacity: int = Field(..., ge=1)


class RoomResponse(BaseModel):
    """Room response."""
    id: UUID
    competition_id: UUID
    name: str
    capacity: int


class RoomListResponse(BaseModel):
    """List of rooms."""
    rooms: list[RoomResponse]
