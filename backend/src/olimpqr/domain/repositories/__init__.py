"""Repository interfaces (abstract base classes)."""

from .user_repository import UserRepository
from .participant_repository import ParticipantRepository
from .competition_repository import CompetitionRepository
from .registration_repository import RegistrationRepository
from .entry_token_repository import EntryTokenRepository
from .attempt_repository import AttemptRepository
from .scan_repository import ScanRepository
from .audit_log_repository import AuditLogRepository
from .institution_repository import InstitutionRepository
from .room_repository import RoomRepository
from .seat_assignment_repository import SeatAssignmentRepository
from .document_repository import DocumentRepository
from .participant_event_repository import ParticipantEventRepository
from .answer_sheet_repository import AnswerSheetRepository

__all__ = [
    "UserRepository",
    "ParticipantRepository",
    "CompetitionRepository",
    "RegistrationRepository",
    "EntryTokenRepository",
    "AttemptRepository",
    "ScanRepository",
    "AuditLogRepository",
    "InstitutionRepository",
    "RoomRepository",
    "SeatAssignmentRepository",
    "DocumentRepository",
    "ParticipantEventRepository",
    "AnswerSheetRepository",
]
