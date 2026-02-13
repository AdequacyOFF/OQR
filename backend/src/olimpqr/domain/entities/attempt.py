"""Attempt entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects import AttemptStatus, TokenHash


@dataclass
class Attempt:
    """Attempt entity - represents an answer sheet.

    Attributes:
        id: Unique identifier
        registration_id: Reference to Registration
        variant_number: Test variant number (1 to N)
        sheet_token_hash: HMAC hash of the sheet QR code token
        status: Attempt status
        score_total: Total score (None until scored)
        confidence: OCR confidence (None if manually scored)
        pdf_file_path: Path to PDF in MinIO storage
        created_at: When attempt was created
        updated_at: When attempt was last updated
    """
    registration_id: UUID
    variant_number: int
    sheet_token_hash: TokenHash
    id: UUID = field(default_factory=uuid4)
    status: AttemptStatus = AttemptStatus.PRINTED
    score_total: int | None = None
    confidence: float | None = None
    pdf_file_path: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.sheet_token_hash, TokenHash):
            raise TypeError("sheet_token_hash must be a TokenHash instance")
        if self.variant_number < 1:
            raise ValueError("Variant number must be positive")

    def mark_scanned(self):
        """Mark attempt as scanned (scan uploaded, OCR processing)."""
        if self.status != AttemptStatus.PRINTED:
            raise ValueError("Can only scan printed attempts")
        self.status = AttemptStatus.SCANNED
        self.updated_at = datetime.utcnow()

    def apply_score(self, score: int, confidence: float | None = None):
        """Apply score to attempt.

        Args:
            score: Total score value
            confidence: OCR confidence (None if manually entered)
        """
        if not self.status.can_apply_score:
            raise ValueError(f"Cannot apply score in status {self.status}")
        if score < 0:
            raise ValueError("Score cannot be negative")
        if confidence is not None and not (0.0 <= confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")

        self.score_total = score
        self.confidence = confidence
        self.status = AttemptStatus.SCORED
        self.updated_at = datetime.utcnow()

    def publish(self):
        """Publish attempt (make visible in results)."""
        if not self.status.has_score:
            raise ValueError("Cannot publish attempt without score")
        self.status = AttemptStatus.PUBLISHED
        self.updated_at = datetime.utcnow()

    def invalidate(self):
        """Invalidate attempt (cheating, technical issues, etc.)."""
        self.status = AttemptStatus.INVALIDATED
        self.updated_at = datetime.utcnow()

    @property
    def is_valid(self) -> bool:
        """Check if attempt is not invalidated."""
        return self.status != AttemptStatus.INVALIDATED

    @property
    def has_score(self) -> bool:
        """Check if score has been applied."""
        return self.score_total is not None
