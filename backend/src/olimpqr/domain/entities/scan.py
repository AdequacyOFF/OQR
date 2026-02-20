"""Scan entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Scan:
    """Scan entity - represents an uploaded scan of an answer sheet.

    Attributes:
        id: Unique identifier
        attempt_id: Reference to Attempt
        file_path: Path to scan file in MinIO storage
        ocr_score: Score extracted by OCR (None if not processed yet)
        ocr_confidence: OCR confidence level (None if not processed yet)
        ocr_raw_text: Raw text extracted by OCR
        verified_by: User who manually verified the score (None if not verified)
        uploaded_by: User who uploaded the scan
        created_at: When scan was uploaded
        updated_at: When scan was last updated
    """
    attempt_id: UUID | None
    file_path: str
    uploaded_by: UUID
    id: UUID = field(default_factory=uuid4)
    answer_sheet_id: UUID | None = None
    ocr_score: int | None = None
    ocr_confidence: float | None = None
    ocr_raw_text: str | None = None
    verified_by: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.file_path:
            raise ValueError("Путь к файлу не может быть пустым")

    def update_ocr_result(self, score: int | None, confidence: float | None, raw_text: str):
        """Update OCR processing result.

        Args:
            score: Extracted score (None if extraction failed)
            confidence: OCR confidence level
            raw_text: Raw text extracted from score field
        """
        if score is not None and score < 0:
            raise ValueError("OCR балл не может быть отрицательным")
        if confidence is not None and not (0.0 <= confidence <= 1.0):
            raise ValueError("Уверенность должна быть от 0.0 до 1.0")

        self.ocr_score = score
        self.ocr_confidence = confidence
        self.ocr_raw_text = raw_text
        self.updated_at = datetime.utcnow()

    def verify(self, verified_by: UUID, corrected_score: int | None = None):
        """Manually verify and optionally correct the OCR score.

        Args:
            verified_by: User who verified the score
            corrected_score: Corrected score (if OCR was wrong)
        """
        if corrected_score is not None:
            if corrected_score < 0:
                raise ValueError("Исправленный балл не может быть отрицательным")
            self.ocr_score = corrected_score

        self.verified_by = verified_by
        self.updated_at = datetime.utcnow()

    @property
    def is_processed(self) -> bool:
        """Check if OCR processing is complete."""
        return self.ocr_raw_text is not None

    @property
    def is_verified(self) -> bool:
        """Check if scan has been manually verified."""
        return self.verified_by is not None

    @property
    def has_valid_score(self) -> bool:
        """Check if scan has a valid extracted score."""
        return self.ocr_score is not None and self.ocr_confidence is not None
