"""Document entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Document:
    """Document entity - uploaded document for a participant.

    Attributes:
        id: Unique identifier
        participant_id: Reference to Participant
        file_path: Path to file in storage
        file_type: MIME type or document type description
        created_at: When document was uploaded
    """
    participant_id: UUID
    file_path: str
    file_type: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.file_path:
            raise ValueError("Путь к файлу не может быть пустым")
        if not self.file_type:
            raise ValueError("Тип файла не может быть пустым")
