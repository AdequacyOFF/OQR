"""Repository interfaces (abstract base classes)."""

from .user_repository import UserRepository
from .participant_repository import ParticipantRepository
from .competition_repository import CompetitionRepository
from .registration_repository import RegistrationRepository
from .entry_token_repository import EntryTokenRepository
from .attempt_repository import AttemptRepository
from .scan_repository import ScanRepository
from .audit_log_repository import AuditLogRepository

__all__ = [
    "UserRepository",
    "ParticipantRepository",
    "CompetitionRepository",
    "RegistrationRepository",
    "EntryTokenRepository",
    "AttemptRepository",
    "ScanRepository",
    "AuditLogRepository",
]
