"""Admin API endpoints."""

from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    UserRepositoryImpl,
    AuditLogRepositoryImpl,
    CompetitionRepositoryImpl,
    ScanRepositoryImpl,
    RegistrationRepositoryImpl,
    ParticipantRepositoryImpl,
    EntryTokenRepositoryImpl,
)
from ....infrastructure.security import hash_password
from ....domain.entities import User
from ....domain.value_objects import UserRole
from ....domain.services import TokenService
from ....application.use_cases.registration.register_for_competition import (
    RegisterForCompetitionUseCase,
)
from ...schemas.admin_schemas import (
    CreateStaffRequest,
    UpdateUserRequest,
    UserListResponse,
    AdminUserResponse,
    AuditLogEntry,
    AuditLogListResponse,
    StatisticsResponse,
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminRegistrationItem,
    AdminRegistrationListResponse,
)
from ...dependencies import require_role

router = APIRouter()


# --- User Management ---

@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    role: Optional[UserRole] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all users with optional role filter."""
    user_repo = UserRepositoryImpl(db)

    if role:
        users = await user_repo.get_by_role(role, skip=skip, limit=limit)
    else:
        users = await user_repo.get_all(skip=skip, limit=limit)

    items = [
        AdminUserResponse(
            id=u.id,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]
    return UserListResponse(items=items, total=len(items))


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_user(
    body: CreateStaffRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Create a user account (participant / admitter / scanner / admin)."""
    user_repo = UserRepositoryImpl(db)

    if await user_repo.exists_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email уже используется")

    # Validate participant-specific fields
    if body.role == UserRole.PARTICIPANT:
        if not body.full_name or len(body.full_name.strip()) < 2:
            raise HTTPException(status_code=400, detail="ФИО обязательно для участников (минимум 2 символа)")
        if not body.school or len(body.school.strip()) < 2:
            raise HTTPException(status_code=400, detail="Учебное учреждение обязательно для участников (минимум 2 символа)")

    from uuid import uuid4

    user = User(
        id=uuid4(),
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    user = await user_repo.create(user)

    # Create participant profile if role is participant
    if body.role == UserRole.PARTICIPANT:
        from ....domain.entities import Participant
        participant_repo = ParticipantRepositoryImpl(db)

        participant = Participant(
            id=uuid4(),
            user_id=user.id,
            full_name=body.full_name,
            school=body.school,
            grade=body.grade,
            institution_id=body.institution_id,
            dob=body.dob,
        )
        await participant_repo.create(participant)

    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: UUID,
    body: UpdateUserRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Update user attributes (active status, role)."""
    user_repo = UserRepositoryImpl(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if body.is_active is not None:
        if body.is_active:
            user.activate()
        else:
            user.deactivate()

    if body.role is not None:
        user.change_role(body.role)

    await user_repo.update(user)

    return AdminUserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a user (soft delete)."""
    user_repo = UserRepositoryImpl(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя деактивировать себя")

    user.deactivate()
    await user_repo.update(user)


# --- Participants ---

@router.get("/participants")
async def list_participants(
    skip: int = 0,
    limit: int = 1000,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all participants (id, full_name, school) for admin registration."""
    from ....infrastructure.database.models import ParticipantModel

    stmt = (
        select(ParticipantModel)
        .order_by(ParticipantModel.full_name)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    participants = result.scalars().all()

    return {
        "participants": [
            {
                "id": str(p.id),
                "user_id": str(p.user_id),
                "full_name": p.full_name,
                "school": p.school,
            }
            for p in participants
        ]
    }


# --- Audit Log ---

@router.get("/audit-log", response_model=AuditLogListResponse)
async def list_audit_log(
    skip: int = 0,
    limit: int = 50,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List audit log entries with optional filters."""
    audit_repo = AuditLogRepositoryImpl(db)

    if entity_type and entity_id:
        logs = await audit_repo.get_by_entity(entity_type, entity_id, skip=skip, limit=limit)
    elif user_id:
        logs = await audit_repo.get_by_user(user_id, skip=skip, limit=limit)
    else:
        logs = await audit_repo.get_all(skip=skip, limit=limit)

    items = [
        AuditLogEntry(
            id=log.id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            user_id=log.user_id,
            ip_address=log.ip_address,
            details=log.details,
            timestamp=log.timestamp,
        )
        for log in logs
    ]
    return AuditLogListResponse(items=items, total=len(items))


# --- Statistics ---

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Get system statistics for admin dashboard."""
    from sqlalchemy import select, func
    from ....infrastructure.database.models import (
        UserModel,
        CompetitionModel,
        ScanModel,
        RegistrationModel,
        ParticipantModel,
    )

    # Count users
    result = await db.execute(select(func.count()).select_from(UserModel))
    total_users = result.scalar() or 0

    # Count competitions
    result = await db.execute(select(func.count()).select_from(CompetitionModel))
    total_competitions = result.scalar() or 0

    # Count scans
    result = await db.execute(select(func.count()).select_from(ScanModel))
    total_scans = result.scalar() or 0

    # Count registrations
    result = await db.execute(select(func.count()).select_from(RegistrationModel))
    total_registrations = result.scalar() or 0

    # Count participants
    result = await db.execute(select(func.count()).select_from(ParticipantModel))
    total_participants = result.scalar() or 0

    return StatisticsResponse(
        total_competitions=total_competitions,
        total_users=total_users,
        total_scans=total_scans,
        total_registrations=total_registrations,
        total_participants=total_participants,
    )


# --- Registration Management ---

@router.post("/registrations", response_model=AdminRegisterResponse, status_code=status.HTTP_201_CREATED)
async def admin_register_participant(
    body: AdminRegisterRequest,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Admin registers a participant for a competition (bypasses status check)."""
    registration_repo = RegistrationRepositoryImpl(db)
    competition_repo = CompetitionRepositoryImpl(db)
    participant_repo = ParticipantRepositoryImpl(db)
    entry_token_repo = EntryTokenRepositoryImpl(db)
    token_service = TokenService()

    use_case = RegisterForCompetitionUseCase(
        registration_repository=registration_repo,
        competition_repository=competition_repo,
        participant_repository=participant_repo,
        entry_token_repository=entry_token_repo,
        token_service=token_service,
    )

    try:
        result = await use_case.execute(
            participant_id=body.participant_id,
            competition_id=body.competition_id,
            skip_status_check=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return AdminRegisterResponse(
        registration_id=result.registration_id,
        entry_token=result.entry_token,
    )


@router.get("/registrations/{competition_id}", response_model=AdminRegistrationListResponse)
async def list_competition_registrations(
    competition_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """List all registrations for a competition with participant details."""
    from ....infrastructure.database.models import (
        RegistrationModel,
        ParticipantModel,
        EntryTokenModel,
        InstitutionModel,
    )

    stmt = (
        select(RegistrationModel)
        .where(RegistrationModel.competition_id == competition_id)
        .options(
            selectinload(RegistrationModel.entry_token),
            selectinload(RegistrationModel.participant).selectinload(ParticipantModel.institution),
        )
        .order_by(RegistrationModel.created_at)
    )
    result = await db.execute(stmt)
    registrations = result.scalars().all()

    items = []
    for reg in registrations:
        participant = reg.participant
        institution_name = None
        if participant and participant.institution:
            institution_name = participant.institution.name

        entry_token_raw = None
        if reg.entry_token:
            entry_token_raw = reg.entry_token.raw_token

        items.append(
            AdminRegistrationItem(
                registration_id=reg.id,
                participant_id=reg.participant_id,
                participant_name=participant.full_name if participant else "—",
                participant_school=participant.school if participant else "—",
                institution_name=institution_name,
                entry_token=entry_token_raw,
                status=reg.status.value,
            )
        )

    return AdminRegistrationListResponse(items=items, total=len(items))


@router.get("/registrations/{competition_id}/badges-pdf")
async def download_badges_pdf(
    competition_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Download a PDF with QR badges for all registrations, grouped by institution."""
    from ....infrastructure.database.models import (
        RegistrationModel,
        CompetitionModel,
    )
    from ....infrastructure.pdf.badge_generator import BadgeGenerator, BadgeData
    from io import BytesIO

    # Get competition name
    comp_result = await db.execute(
        select(CompetitionModel).where(CompetitionModel.id == competition_id)
    )
    competition = comp_result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Олимпиада не найдена")

    # Get registrations
    from ....infrastructure.database.models import ParticipantModel
    stmt = (
        select(RegistrationModel)
        .where(RegistrationModel.competition_id == competition_id)
        .options(
            selectinload(RegistrationModel.entry_token),
            selectinload(RegistrationModel.participant).selectinload(ParticipantModel.institution),
        )
        .order_by(RegistrationModel.created_at)
    )
    result = await db.execute(stmt)
    registrations = result.scalars().all()

    badges: list[BadgeData] = []
    for reg in registrations:
        participant = reg.participant
        if not participant:
            continue

        entry_token_raw = None
        if reg.entry_token and reg.entry_token.raw_token:
            entry_token_raw = reg.entry_token.raw_token

        if not entry_token_raw:
            continue

        institution_name = ""
        if participant.institution:
            institution_name = participant.institution.name

        badges.append(
            BadgeData(
                name=participant.full_name,
                school=participant.school,
                institution=institution_name,
                qr_token=entry_token_raw,
            )
        )

    # Sort by institution then name
    badges.sort(key=lambda b: (b.institution or "", b.name))

    generator = BadgeGenerator()
    pdf_bytes = generator.generate_badges_pdf(competition.name, badges)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="badges_{competition_id}.pdf"'
        },
    )
