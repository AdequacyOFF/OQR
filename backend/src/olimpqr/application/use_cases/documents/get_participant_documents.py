"""Get participant documents use case."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from ....domain.repositories import DocumentRepository


@dataclass
class DocumentItem:
    id: UUID
    file_path: str
    file_type: str
    created_at: datetime


class GetParticipantDocumentsUseCase:
    """Get all documents for a participant."""

    def __init__(self, document_repository: DocumentRepository):
        self.document_repo = document_repository

    async def execute(self, participant_id: UUID) -> list[DocumentItem]:
        documents = await self.document_repo.get_by_participant(participant_id)
        return [
            DocumentItem(
                id=d.id,
                file_path=d.file_path,
                file_type=d.file_type,
                created_at=d.created_at,
            )
            for d in documents
        ]
