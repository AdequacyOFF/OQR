"""Registration status enumeration."""

from enum import Enum


class RegistrationStatus(str, Enum):
    """Registration status for participant-competition relationship.

    - PENDING: Registration created, entry token generated
    - ADMITTED: Entry QR scanned, participant allowed in
    - COMPLETED: Answer sheet generated and handed to participant
    - CANCELLED: Registration cancelled by admin or participant
    """
    PENDING = "pending"
    ADMITTED = "admitted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    @property
    def is_active(self) -> bool:
        """Check if registration is still active."""
        return self != RegistrationStatus.CANCELLED

    @property
    def can_generate_sheet(self) -> bool:
        """Check if answer sheet can be generated."""
        return self == RegistrationStatus.ADMITTED
