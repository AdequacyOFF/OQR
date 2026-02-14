"""Admin API endpoints."""

from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import (
    UserRepositoryImpl,
    AuditLogRepositoryImpl,
    CompetitionRepositoryImpl,
    ScanRepositoryImpl,
    RegistrationRepositoryImpl,
    ParticipantRepositoryImpl,
)
from ....infrastructure.security import hash_password
from ....domain.entities import User
from ....domain.value_objects import UserRole
from ...schemas.admin_schemas import (
    CreateStaffRequest,
    UpdateUserRequest,
    UserListResponse,
    AdminUserResponse,
    AuditLogEntry,
    AuditLogListResponse,
    StatisticsResponse,
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
        raise HTTPException(status_code=400, detail="Email already in use")

    # Validate participant-specific fields
    if body.role == UserRole.PARTICIPANT:
        if not body.full_name or len(body.full_name.strip()) < 2:
            raise HTTPException(status_code=400, detail="Full name is required for participants (min 2 characters)")
        if not body.school or len(body.school.strip()) < 2:
            raise HTTPException(status_code=400, detail="School is required for participants (min 2 characters)")
        if body.grade is None or not (1 <= body.grade <= 12):
            raise HTTPException(status_code=400, detail="Grade is required for participants (1-12)")

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
        raise HTTPException(status_code=404, detail="User not found")

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
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.deactivate()
    await user_repo.update(user)


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
