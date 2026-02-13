"""Registration entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects import RegistrationStatus


@dataclass
class Registration:
    """Registration entity - links participant to competition.

    Attributes:
        id: Unique identifier
        participant_id: Reference to Participant
        competition_id: Reference to Competition
        status: Registration status
        created_at: When registration was created
        updated_at: When registration was last updated
    """
    participant_id: UUID
    competition_id: UUID
    id: UUID = field(default_factory=uuid4)
    status: RegistrationStatus = RegistrationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def admit(self):
        """Mark participant as admitted (entry QR verified)."""
        if self.status != RegistrationStatus.PENDING:
            raise ValueError("Can only admit from pending status")
        self.status = RegistrationStatus.ADMITTED
        self.updated_at = datetime.utcnow()

    def complete(self):
        """Mark registration as completed (answer sheet generated)."""
        if self.status != RegistrationStatus.ADMITTED:
            raise ValueError("Can only complete from admitted status")
        self.status = RegistrationStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel the registration."""
        if self.status == RegistrationStatus.CANCELLED:
            raise ValueError("Registration is already cancelled")
        self.status = RegistrationStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Check if registration is active."""
        return self.status != RegistrationStatus.CANCELLED

    @property
    def can_generate_sheet(self) -> bool:
        """Check if answer sheet can be generated."""
        return self.status == RegistrationStatus.ADMITTED
