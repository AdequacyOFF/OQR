"""Documents API endpoints."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    DocumentRepositoryImpl,
    ParticipantRepositoryImpl,
)
from ....infrastructure.storage import MinIOStorage
from ....domain.value_objects import UserRole
from ....domain.entities import User
from ....application.use_cases.documents import (
    UploadDocumentUseCase,
    GetParticipantDocumentsUseCase,
)
from ...schemas.document_schemas import DocumentResponse, DocumentListResponse
from ...dependencies import require_role, get_current_active_user
from ....config import settings

router = APIRouter()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document (participant uploads their own docs)."""
    if current_user.role != UserRole.PARTICIPANT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только участники могут загружать документы",
        )

    participant_repo = ParticipantRepositoryImpl(db)
    participant = await participant_repo.get_by_user_id(current_user.id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль участника не найден",
        )

    try:
        file_data = await file.read()
        use_case = UploadDocumentUseCase(
            document_repository=DocumentRepositoryImpl(db),
            participant_repository=participant_repo,
            storage=MinIOStorage(),
        )
        result = await use_case.execute(
            participant_id=participant.id,
            file_data=file_data,
            file_type=file.content_type or "application/octet-stream",
            original_filename=file.filename or "document",
        )
        from datetime import datetime
        return DocumentResponse(
            id=result.id,
            file_path=result.file_path,
            file_type=result.file_type,
            created_at=datetime.utcnow(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/participant/{participant_id}", response_model=DocumentListResponse)
async def get_participant_documents(
    participant_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.ADMITTER, UserRole.INVIGILATOR))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get documents for a participant (admin/admitter/invigilator)."""
    use_case = GetParticipantDocumentsUseCase(
        document_repository=DocumentRepositoryImpl(db),
    )
    results = await use_case.execute(participant_id=participant_id)
    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=d.id,
                file_path=d.file_path,
                file_type=d.file_type,
                created_at=d.created_at,
            )
            for d in results
        ]
    )
