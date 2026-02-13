"""Registration API endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    RegistrationRepositoryImpl,
    CompetitionRepositoryImpl,
    ParticipantRepositoryImpl,
    EntryTokenRepositoryImpl
)
from ....domain.services import TokenService, QRService
from ....domain.value_objects import UserRole
from ....domain.entities import User
from ....application.use_cases.registration import (
    RegisterForCompetitionUseCase,
    GetEntryQRUseCase
)
from ...schemas.registration_schemas import (
    RegisterForCompetitionRequest,
    RegistrationResponse
)
from ...dependencies import require_role, get_current_active_user
from ....config import settings


router = APIRouter()


@router.post("", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_for_competition(
    request: RegisterForCompetitionRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.PARTICIPANT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register current participant for a competition.

    Requires participant role.
    Returns registration with entry_token (shown only once!).
    """
    try:
        # Get participant by user_id
        participant_repo = ParticipantRepositoryImpl(db)
        participant = await participant_repo.get_by_user_id(current_user.id)
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant profile not found"
            )

        # Create repositories
        registration_repo = RegistrationRepositoryImpl(db)
        competition_repo = CompetitionRepositoryImpl(db)
        entry_token_repo = EntryTokenRepositoryImpl(db)
        token_service = TokenService(settings.hmac_secret_key)

        # Create use case
        use_case = RegisterForCompetitionUseCase(
            registration_repo,
            competition_repo,
            participant_repo,
            entry_token_repo,
            token_service
        )

        # Execute
        result = await use_case.execute(
            participant_id=participant.id,
            competition_id=request.competition_id
        )

        # Get registration to return full data
        registration = await registration_repo.get_by_id(result.registration_id)

        return RegistrationResponse(
            id=registration.id,
            participant_id=registration.participant_id,
            competition_id=registration.competition_id,
            status=registration.status,
            created_at=registration.created_at,
            entry_token=result.entry_token  # Only shown once!
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
