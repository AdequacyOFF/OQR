"""List competitions use case."""

from typing import List

from ....domain.entities import Competition
from ....domain.repositories import CompetitionRepository
from ....domain.value_objects import CompetitionStatus


class ListCompetitionsUseCase:
    """Use case for listing competitions."""

    def __init__(self, competition_repository: CompetitionRepository):
        self.competition_repository = competition_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: CompetitionStatus | None = None
    ) -> List[Competition]:
        """List competitions with optional status filter.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Optional status filter

        Returns:
            List of competition entities
        """
        if status_filter:
            return await self.competition_repository.get_by_status(
                status=status_filter,
                skip=skip,
                limit=limit
            )
        else:
            return await self.competition_repository.get_all(
                skip=skip,
                limit=limit
            )
