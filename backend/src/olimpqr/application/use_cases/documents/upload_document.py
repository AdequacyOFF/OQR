"""Upload document use case."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.entities import Document
from ....domain.repositories import DocumentRepository, ParticipantRepository
from ....infrastructure.storage import MinIOStorage
from ....config import settings


@dataclass
class UploadDocumentResult:
    id: UUID
    file_path: str
    file_type: str


class UploadDocumentUseCase:
    """Upload a document for a participant."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        participant_repository: ParticipantRepository,
        storage: MinIOStorage,
    ):
        self.document_repo = document_repository
        self.participant_repo = participant_repository
        self.storage = storage

    async def execute(
        self,
        participant_id: UUID,
        file_data: bytes,
        file_type: str,
        original_filename: str,
    ) -> UploadDocumentResult:
        participant = await self.participant_repo.get_by_id(participant_id)
        if not participant:
            raise ValueError("Участник не найден")

        # Upload to storage
        object_name = f"documents/{participant_id}/{original_filename}"
        self.storage.upload_file(
            bucket=settings.minio_bucket_sheets,
            object_name=object_name,
            data=file_data,
            content_type=file_type,
        )

        # Create document record
        document = Document(
            participant_id=participant_id,
            file_path=object_name,
            file_type=file_type,
        )
        await self.document_repo.create(document)

        return UploadDocumentResult(
            id=document.id,
            file_path=document.file_path,
            file_type=document.file_type,
        )
