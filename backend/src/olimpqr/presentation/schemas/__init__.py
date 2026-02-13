"""Pydantic schemas for API requests and responses."""

from .auth_schemas import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse
)
from .competition_schemas import (
    CreateCompetitionRequest,
    UpdateCompetitionRequest,
    CompetitionResponse,
    CompetitionListResponse
)
from .registration_schemas import (
    RegisterForCompetitionRequest,
    RegistrationResponse,
    EntryQRResponse,
)
from .admission_schemas import (
    VerifyEntryQRRequest,
    VerifyEntryQRResponse,
    ApproveAdmissionRequest,
    ApproveAdmissionResponse,
)

__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "AuthResponse",
    "UserResponse",
    "CreateCompetitionRequest",
    "UpdateCompetitionRequest",
    "CompetitionResponse",
    "CompetitionListResponse",
    "RegisterForCompetitionRequest",
    "RegistrationResponse",
    "EntryQRResponse",
    "VerifyEntryQRRequest",
    "VerifyEntryQRResponse",
    "ApproveAdmissionRequest",
    "ApproveAdmissionResponse",
]
