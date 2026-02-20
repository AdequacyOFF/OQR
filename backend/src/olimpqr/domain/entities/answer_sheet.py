"""Answer sheet entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from ..value_objects import SheetKind
from ..value_objects.token import TokenHash


@dataclass
class AnswerSheet:
    """Answer sheet entity - represents a physical answer sheet with QR token.

    Attributes:
        id: Unique identifier
        attempt_id: Reference to Attempt
        sheet_token_hash: HMAC hash of the sheet QR code token
        kind: Primary or extra sheet
        pdf_file_path: Path to PDF in storage
        created_at: When sheet was created
    """
    attempt_id: UUID
    sheet_token_hash: TokenHash
    kind: SheetKind
    id: UUID = field(default_factory=uuid4)
    pdf_file_path: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.sheet_token_hash, TokenHash):
            raise TypeError("sheet_token_hash must be a TokenHash instance")
        if not isinstance(self.kind, SheetKind):
            raise TypeError("kind must be a SheetKind instance")
