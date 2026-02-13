"""Use cases - application business logic."""

from .auth import RegisterUserUseCase, LoginUserUseCase
from .competitions import (
    CreateCompetitionUseCase,
    GetCompetitionUseCase,
    ListCompetitionsUseCase,
    UpdateCompetitionUseCase,
    DeleteCompetitionUseCase,
    ChangeCompetitionStatusUseCase
)
from .registration import (
    RegisterForCompetitionUseCase,
    GetEntryQRUseCase,
    GetParticipantRegistrationsUseCase
)
from .admission import (
    VerifyEntryQRUseCase,
    ApproveAdmissionUseCase,
)

__all__ = [
    "RegisterUserUseCase",
    "LoginUserUseCase",
    "CreateCompetitionUseCase",
    "GetCompetitionUseCase",
    "ListCompetitionsUseCase",
    "UpdateCompetitionUseCase",
    "DeleteCompetitionUseCase",
    "ChangeCompetitionStatusUseCase",
    "RegisterForCompetitionUseCase",
    "GetEntryQRUseCase",
    "GetParticipantRegistrationsUseCase",
    "VerifyEntryQRUseCase",
    "ApproveAdmissionUseCase",
]
