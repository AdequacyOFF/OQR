"""Attempt status enumeration."""

from enum import Enum


class AttemptStatus(str, Enum):
    """Status of an answer sheet attempt.

    - PRINTED: Answer sheet generated and given to participant
    - SCANNED: Scan uploaded, OCR processing queued/in progress
    - SCORED: Score extracted (OCR or manual) and applied
    - PUBLISHED: Results made public
    - INVALIDATED: Attempt invalidated (cheating, technical issues, etc.)
    """
    PRINTED = "printed"
    SCANNED = "scanned"
    SCORED = "scored"
    PUBLISHED = "published"
    INVALIDATED = "invalidated"

    @property
    def is_valid(self) -> bool:
        """Check if attempt is not invalidated."""
        return self != AttemptStatus.INVALIDATED

    @property
    def can_upload_scan(self) -> bool:
        """Check if scan can be uploaded."""
        return self == AttemptStatus.PRINTED

    @property
    def can_apply_score(self) -> bool:
        """Check if score can be applied."""
        return self in (AttemptStatus.PRINTED, AttemptStatus.SCANNED, AttemptStatus.SCORED)

    @property
    def has_score(self) -> bool:
        """Check if score has been applied."""
        return self in (AttemptStatus.SCORED, AttemptStatus.PUBLISHED)
