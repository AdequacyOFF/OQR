"""Registration API endpoints."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    RegistrationRepositoryImpl,
    CompetitionRepositoryImpl,
    ParticipantRepositoryImpl,
    EntryTokenRepositoryImpl,
    AttemptRepositoryImpl
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
    RegistrationResponse,
    RegistrationListResponse
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
                detail="Профиль участника не найден"
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


@router.get("", response_model=RegistrationListResponse)
async def get_my_registrations(
    current_user: Annotated[User, Depends(require_role(UserRole.PARTICIPANT))],
    db: Annotated[AsyncSession, Depends(get_db)],
    skip: int = 0,
    limit: int = 100
):
    """Get current participant's registrations.

    Requires participant role.
    Returns list of all registrations for the current user.
    """
    # Get participant by user_id
    participant_repo = ParticipantRepositoryImpl(db)
    participant = await participant_repo.get_by_user_id(current_user.id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль участника не найден"
        )

    # Get registrations
    registration_repo = RegistrationRepositoryImpl(db)
    registrations = await registration_repo.get_by_participant_id(
        participant.id, skip=skip, limit=limit
    )

    # Get attempts and entry tokens for each registration
    attempt_repo = AttemptRepositoryImpl(db)
    entry_token_repo = EntryTokenRepositoryImpl(db)
    items = []
    for r in registrations:
        # Try to get attempt for this registration
        attempt = await attempt_repo.get_by_registration(r.id)

        # Get entry token for this registration
        entry_token = await entry_token_repo.get_by_registration(r.id)
        raw_token = None
        if entry_token and entry_token.raw_token:
            raw_token = entry_token.raw_token
        elif entry_token:
            # Fallback to registration_id for old registrations
            raw_token = str(r.id)

        items.append(
            RegistrationResponse(
                id=r.id,
                participant_id=r.participant_id,
                competition_id=r.competition_id,
                status=r.status,
                created_at=r.created_at,
                entry_token=raw_token,
                attempt_id=attempt.id if attempt else None,
                variant_number=attempt.variant_number if attempt else None,
                final_score=attempt.score_total if attempt else None
            )
        )

    return RegistrationListResponse(
        items=items,
        total=len(registrations)
    )


@router.get("/{registration_id}", response_model=RegistrationResponse)
async def get_registration(
    registration_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.PARTICIPANT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Get registration by ID.

    Requires participant role.
    User can only access their own registrations.
    Returns entry_token if available.
    """
    # Get participant by user_id
    participant_repo = ParticipantRepositoryImpl(db)
    participant = await participant_repo.get_by_user_id(current_user.id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль участника не найден"
        )

    # Get registration
    registration_repo = RegistrationRepositoryImpl(db)
    registration = await registration_repo.get_by_id(registration_id)

    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Регистрация не найдена"
        )

    # Check ownership
    if registration.participant_id != participant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )

    # Get entry token if available
    entry_token_repo = EntryTokenRepositoryImpl(db)
    entry_token = await entry_token_repo.get_by_registration(registration_id)

    # Use raw_token if available, otherwise fallback to registration_id
    # (for backward compatibility with old registrations)
    raw_token = None
    if entry_token and entry_token.raw_token:
        raw_token = entry_token.raw_token
    else:
        # Fallback to registration_id for old registrations
        raw_token = str(registration.id)

    return RegistrationResponse(
        id=registration.id,
        participant_id=registration.participant_id,
        competition_id=registration.competition_id,
        status=registration.status,
        created_at=registration.created_at,
        entry_token=raw_token
    )


@router.post("/{registration_id}/refresh-token", response_model=RegistrationResponse)
async def refresh_entry_token(
    registration_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.PARTICIPANT))],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh (regenerate) entry token for a registration.

    Use this if the token has expired.
    Cannot refresh if token has already been used (admission completed).
    """
    from datetime import datetime, timedelta

    # Get participant
    participant_repo = ParticipantRepositoryImpl(db)
    participant = await participant_repo.get_by_user_id(current_user.id)
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль участника не найден"
        )

    # Get registration
    registration_repo = RegistrationRepositoryImpl(db)
    registration = await registration_repo.get_by_id(registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Регистрация не найдена"
        )

    # Check ownership
    if registration.participant_id != participant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ запрещён"
        )

    # Get existing entry token
    entry_token_repo = EntryTokenRepositoryImpl(db)
    entry_token = await entry_token_repo.get_by_registration(registration_id)
    if not entry_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Входной токен не найден"
        )

    # Check if already used
    if entry_token.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно обновить токен - допуск уже завершён"
        )

    # Generate new token
    token_service = TokenService(settings.hmac_secret_key)
    new_token = token_service.generate_token()

    # Update entry token
    entry_token.token_hash = new_token.hash
    entry_token.raw_token = new_token.raw
    entry_token.expires_at = datetime.utcnow() + timedelta(hours=settings.entry_token_expire_hours)

    await entry_token_repo.update(entry_token)

    return RegistrationResponse(
        id=registration.id,
        participant_id=registration.participant_id,
        competition_id=registration.competition_id,
        status=registration.status,
        created_at=registration.created_at,
        entry_token=new_token.raw
    )
