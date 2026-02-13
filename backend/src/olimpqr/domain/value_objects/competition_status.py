"""Competition status enumeration."""

from enum import Enum


class CompetitionStatus(str, Enum):
    """Competition lifecycle status.

    - DRAFT: Competition is being prepared
    - REGISTRATION_OPEN: Participants can register
    - IN_PROGRESS: Competition is happening, admission in progress
    - CHECKING: All attempts submitted, scoring in progress
    - PUBLISHED: Results are public
    """
    DRAFT = "draft"
    REGISTRATION_OPEN = "registration_open"
    IN_PROGRESS = "in_progress"
    CHECKING = "checking"
    PUBLISHED = "published"

    @property
    def allows_registration(self) -> bool:
        """Check if participants can register."""
        return self == CompetitionStatus.REGISTRATION_OPEN

    @property
    def allows_admission(self) -> bool:
        """Check if admitters can verify entry QR codes."""
        return self == CompetitionStatus.IN_PROGRESS

    @property
    def allows_score_changes(self) -> bool:
        """Check if scores can still be modified."""
        return self in (CompetitionStatus.IN_PROGRESS, CompetitionStatus.CHECKING)

    @property
    def results_visible(self) -> bool:
        """Check if results are visible to participants."""
        return self == CompetitionStatus.PUBLISHED
