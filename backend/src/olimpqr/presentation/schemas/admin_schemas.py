"""Admin-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Any, Dict, Optional

from ...domain.value_objects import UserRole


class CreateStaffRequest(BaseModel):
    """Create a staff user (admitter / scanner / admin / participant)."""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole
    full_name: Optional[str] = None
    school: Optional[str] = None
    grade: Optional[int] = Field(None, ge=1, le=12)


class UpdateUserRequest(BaseModel):
    """Update user fields."""
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserListResponse(BaseModel):
    """Paginated list of users."""
    items: list["AdminUserResponse"]
    total: int


class AdminUserResponse(BaseModel):
    """User response for admin panel."""
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime


class AuditLogEntry(BaseModel):
    """Single audit log entry."""
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    user_id: Optional[UUID]
    ip_address: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated list of audit log entries."""
    items: list[AuditLogEntry]
    total: int


class StatisticsResponse(BaseModel):
    """System statistics for admin dashboard."""
    total_competitions: int
    total_users: int
    total_scans: int
    total_registrations: int
    total_participants: int
