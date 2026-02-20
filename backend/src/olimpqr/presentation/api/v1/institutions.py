"""Institutions API endpoints."""

from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.repositories import InstitutionRepositoryImpl
from ....domain.value_objects import UserRole
from ....domain.entities import User
from ....application.use_cases.institutions import (
    CreateInstitutionUseCase,
    ListInstitutionsUseCase,
    SearchInstitutionsUseCase,
)
from ...schemas.institution_schemas import (
    CreateInstitutionRequest,
    InstitutionResponse,
    InstitutionListResponse,
)
from ...dependencies import require_role

router = APIRouter()


@router.get("/search", response_model=list[InstitutionResponse])
async def search_institutions(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Search institutions by name (public endpoint)."""
    use_case = SearchInstitutionsUseCase(
        institution_repository=InstitutionRepositoryImpl(db),
    )
    results = await use_case.execute(query=q, limit=limit)
    return [
        InstitutionResponse(id=r.id, name=r.name, short_name=r.short_name, city=r.city)
        for r in results
    ]


@router.get("", response_model=InstitutionListResponse)
async def list_institutions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """List all institutions (public endpoint)."""
    use_case = ListInstitutionsUseCase(
        institution_repository=InstitutionRepositoryImpl(db),
    )
    results = await use_case.execute(skip=skip, limit=limit)
    return InstitutionListResponse(
        institutions=[
            InstitutionResponse(id=r.id, name=r.name, short_name=r.short_name, city=r.city)
            for r in results
        ],
        total=len(results),
    )


@router.post("", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    request_body: CreateInstitutionRequest,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new institution (admin only)."""
    try:
        use_case = CreateInstitutionUseCase(
            institution_repository=InstitutionRepositoryImpl(db),
        )
        result = await use_case.execute(
            name=request_body.name,
            short_name=request_body.short_name,
            city=request_body.city,
        )
        return InstitutionResponse(
            id=result.id,
            name=result.name,
            short_name=result.short_name,
            city=result.city,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: UUID,
    current_user: Annotated[User, Depends(require_role(UserRole.ADMIN))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an institution (admin only)."""
    repo = InstitutionRepositoryImpl(db)
    deleted = await repo.delete(institution_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Учреждение не найдено",
        )
