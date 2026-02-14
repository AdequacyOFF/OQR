"""Auth-related Pydantic schemas."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID

from ...domain.value_objects import UserRole


class RegisterRequest(BaseModel):
    """Request schema for user registration (participant only)."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=2, description="Full name (required)")
    school: str = Field(..., min_length=2, description="School name (required)")
    grade: int = Field(..., ge=1, le=12, description="Grade 1-12 (required)")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "student@example.com",
                    "password": "securepass123",
                    "role": "participant",
                    "full_name": "Иван Иванов",
                    "school": "Школа №1",
                    "grade": 10
                }
            ]
        }
    }


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "student@example.com",
                    "password": "securepass123"
                }
            ]
        }
    }


class AuthResponse(BaseModel):
    """Response schema for authentication (login/register)."""
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    role: UserRole

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user_id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "student@example.com",
                    "role": "participant"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: UUID
    email: str
    role: UserRole
    is_active: bool

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "student@example.com",
                    "role": "participant",
                    "is_active": True
                }
            ]
        }
    }
