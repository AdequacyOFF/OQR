"""Get competition use case."""

from uuid import UUID

from ....domain.entities import Competition
from ....domain.repositories import CompetitionRepository


class GetCompetitionUseCase:
    """Use case for getting a competition by ID."""

    def __init__(self, competition_repository: CompetitionRepository):
        self.competition_repository = competition_repository

    async def execute(self, competition_id: UUID) -> Competition | None:
        """Get a competition by ID.

        Args:
            competition_id: Competition ID

        Returns:
            Competition entity or None if not found
        """
        return await self.competition_repository.get_by_id(competition_id)
