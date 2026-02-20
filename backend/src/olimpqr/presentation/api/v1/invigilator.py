"""Invigilator API endpoints."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    ParticipantEventRepositoryImpl,
    AttemptRepositoryImpl,
    AnswerSheetRepositoryImpl,
)
from ....infrastructure.storage import MinIOStorage
from ....infrastructure.pdf import SheetGenerator
from ....domain.value_objects import UserRole
from ....domain.services import TokenService
from ....domain.entities import User
from ....application.use_cases.invigilator import (
    RecordEventUseCase,
    IssueExtraSheetUseCase,
    GetAttemptEventsUseCase,
)
from ...schemas.invigilator_schemas import (
    RecordEventRequest,
    RecordEventResponse,
    IssueExtraSheetRequest,
    IssueExtraSheetResponse,
    EventItem,
    AttemptEventsResponse,
)
from ...dependencies import require_role
from ....config import settings

router = APIRouter()


@router.post("/events", response_model=RecordEventResponse, status_code=status.HTTP_201_CREATED)
async def record_event(
    request_body: RecordEventRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.INVIGILATOR, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record a participant event (invigilator)."""
    try:
        use_case = RecordEventUseCase(
            event_repository=ParticipantEventRepositoryImpl(db),
            attempt_repository=AttemptRepositoryImpl(db),
        )
        result = await use_case.execute(
            attempt_id=request_body.attempt_id,
            event_type=request_body.event_type,
            recorded_by=current_user.id,
            timestamp=request_body.timestamp,
        )
        return RecordEventResponse(
            id=result.id,
            attempt_id=result.attempt_id,
            event_type=result.event_type,
            timestamp=result.timestamp,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/extra-sheet", response_model=IssueExtraSheetResponse, status_code=status.HTTP_201_CREATED)
async def issue_extra_sheet(
    request_body: IssueExtraSheetRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.INVIGILATOR, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Issue an extra answer sheet for an attempt (invigilator)."""
    try:
        use_case = IssueExtraSheetUseCase(
            answer_sheet_repository=AnswerSheetRepositoryImpl(db),
            attempt_repository=AttemptRepositoryImpl(db),
            token_service=TokenService(settings.hmac_secret_key),
            sheet_generator=SheetGenerator(),
            storage=MinIOStorage(),
        )
        result = await use_case.execute(attempt_id=request_body.attempt_id)
        return IssueExtraSheetResponse(
            answer_sheet_id=result.answer_sheet_id,
            sheet_token=result.sheet_token,
            pdf_url=result.pdf_url,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/attempt/{attempt_id}/events", response_model=AttemptEventsResponse)
async def get_attempt_events(
    attempt_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.INVIGILATOR, UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get all events for an attempt (invigilator)."""
    use_case = GetAttemptEventsUseCase(
        event_repository=ParticipantEventRepositoryImpl(db),
    )
    results = await use_case.execute(attempt_id=attempt_id)
    return AttemptEventsResponse(
        events=[
            EventItem(
                id=e.id,
                attempt_id=e.attempt_id,
                event_type=e.event_type,
                timestamp=e.timestamp,
                recorded_by=e.recorded_by,
            )
            for e in results
        ]
    )
