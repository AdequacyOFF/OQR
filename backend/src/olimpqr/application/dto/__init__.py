"""Data Transfer Objects."""

from .auth_dto import RegisterUserDTO, LoginUserDTO, AuthResponseDTO
from .competition_dto import CreateCompetitionDTO, UpdateCompetitionDTO, CompetitionDTO

__all__ = [
    "RegisterUserDTO",
    "LoginUserDTO",
    "AuthResponseDTO",
    "CreateCompetitionDTO",
    "UpdateCompetitionDTO",
    "CompetitionDTO",
]
