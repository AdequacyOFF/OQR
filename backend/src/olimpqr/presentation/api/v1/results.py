"""Public results API endpoints (no auth required)."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....infrastructure.database import get_db
from ....infrastructure.database.models import (
    CompetitionModel,
    RegistrationModel,
    AttemptModel,
    ParticipantModel,
)
from ....domain.value_objects import CompetitionStatus, AttemptStatus
from ...schemas.result_schemas import ResultEntry, CompetitionResultsResponse

router = APIRouter()


@router.get("/{competition_id}", response_model=CompetitionResultsResponse)
async def get_published_results(
    competition_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get published results for a competition.

    Only works for competitions with status = PUBLISHED.
    Results are sorted by score descending with rank assigned.
    """
    # Get competition
    result = await db.execute(
        select(CompetitionModel).where(CompetitionModel.id == competition_id)
    )
    competition = result.scalar_one_or_none()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    if competition.status != CompetitionStatus.PUBLISHED:
        raise HTTPException(status_code=403, detail="Results not yet published")

    # Query attempts with participant info, sorted by score
    stmt = (
        select(
            AttemptModel.score_total,
            ParticipantModel.full_name,
            ParticipantModel.school,
            ParticipantModel.grade,
        )
        .join(RegistrationModel, AttemptModel.registration_id == RegistrationModel.id)
        .join(ParticipantModel, RegistrationModel.participant_id == ParticipantModel.id)
        .where(RegistrationModel.competition_id == competition_id)
        .where(AttemptModel.status.in_([AttemptStatus.SCORED, AttemptStatus.PUBLISHED]))
        .where(AttemptModel.score_total.isnot(None))
        .order_by(AttemptModel.score_total.desc())
    )
    rows = await db.execute(stmt)
    rows = rows.all()

    entries: list[ResultEntry] = []
    for rank, row in enumerate(rows, start=1):
        entries.append(
            ResultEntry(
                rank=rank,
                participant_name=row.full_name,
                school=row.school,
                grade=row.grade,
                score=row.score_total,
                max_score=competition.max_score,
            )
        )

    return CompetitionResultsResponse(
        competition_id=competition.id,
        competition_name=competition.name,
        results=entries,
        total_participants=len(entries),
    )
