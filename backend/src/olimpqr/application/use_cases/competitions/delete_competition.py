"""Delete competition use case."""

from uuid import UUID

from ....domain.repositories import CompetitionRepository


class DeleteCompetitionUseCase:
    """Use case for deleting a competition."""

    def __init__(self, competition_repository: CompetitionRepository):
        self.competition_repository = competition_repository

    async def execute(self, competition_id: UUID) -> bool:
        """Delete a competition.

        Args:
            competition_id: Competition ID

        Returns:
            True if deleted, False if not found
        """
        return await self.competition_repository.delete(competition_id)
