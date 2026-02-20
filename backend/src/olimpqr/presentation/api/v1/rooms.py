"""Rooms API endpoints."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import RoomRepositoryImpl, CompetitionRepositoryImpl
from ....domain.value_objects import UserRole
from ....domain.entities import User
from ....application.use_cases.rooms import (
    CreateRoomUseCase,
    ListRoomsUseCase,
    DeleteRoomUseCase,
)
from ...schemas.room_schemas import (
    CreateRoomRequest,
    RoomResponse,
    RoomListResponse,
)
from ...dependencies import require_role

router = APIRouter()


@router.get("/{competition_id}", response_model=RoomListResponse)
async def list_rooms(
    competition_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.ADMITTER, UserRole.INVIGILATOR))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List rooms for a competition."""
    use_case = ListRoomsUseCase(room_repository=RoomRepositoryImpl(db))
    results = await use_case.execute(competition_id=competition_id)
    return RoomListResponse(
        rooms=[
            RoomResponse(id=r.id, competition_id=r.competition_id, name=r.name, capacity=r.capacity)
            for r in results
        ]
    )


@router.post("/{competition_id}", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    competition_id: UUID,
    request_body: CreateRoomRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a room for a competition (admin only)."""
    try:
        use_case = CreateRoomUseCase(
            room_repository=RoomRepositoryImpl(db),
            competition_repository=CompetitionRepositoryImpl(db),
        )
        result = await use_case.execute(
            competition_id=competition_id,
            name=request_body.name,
            capacity=request_body.capacity,
        )
        return RoomResponse(
            id=result.id,
            competition_id=result.competition_id,
            name=result.name,
            capacity=result.capacity,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Аудитория с таким названием уже существует в этой олимпиаде",
        )


@router.delete("/room/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a room (admin only)."""
    use_case = DeleteRoomUseCase(room_repository=RoomRepositoryImpl(db))
    deleted = await use_case.execute(room_id=room_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудитория не найдена",
        )
