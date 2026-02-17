"""Change competition status use case."""

from uuid import UUID

from ....domain.entities import Competition
from ....domain.repositories import CompetitionRepository
from ....domain.value_objects import CompetitionStatus


class ChangeCompetitionStatusUseCase:
    """Use case for changing competition status."""

    def __init__(self, competition_repository: CompetitionRepository):
        self.competition_repository = competition_repository

    async def execute(self, competition_id: UUID, new_status: CompetitionStatus) -> Competition:
        """Change competition status using entity methods.

        Args:
            competition_id: Competition ID
            new_status: New status to transition to

        Returns:
            Updated competition entity

        Raises:
            ValueError: If competition not found or invalid status transition
        """
        # Get existing competition
        competition = await self.competition_repository.get_by_id(competition_id)
        if not competition:
            raise ValueError(f"Олимпиада с id {competition_id} не найдена")

        # Use entity methods for status transitions
        if new_status == CompetitionStatus.REGISTRATION_OPEN:
            competition.open_registration()
        elif new_status == CompetitionStatus.IN_PROGRESS:
            competition.start_competition()
        elif new_status == CompetitionStatus.CHECKING:
            competition.start_checking()
        elif new_status == CompetitionStatus.PUBLISHED:
            competition.publish_results()
        else:
            raise ValueError(f"Недопустимый переход статуса к {new_status}")

        # Save to repository
        competition = await self.competition_repository.update(competition)

        return competition
