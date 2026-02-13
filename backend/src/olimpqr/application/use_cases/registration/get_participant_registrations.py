"""Get participant registrations use case."""

from uuid import UUID
from typing import List
from dataclasses import dataclass

from ....domain.entities import Registration, Competition
from ....domain.repositories import RegistrationRepository, CompetitionRepository


@dataclass
class RegistrationWithCompetition:
    """Registration with competition details."""
    registration: Registration
    competition: Competition


class GetParticipantRegistrationsUseCase:
    """Use case for getting participant's registrations."""

    def __init__(
        self,
        registration_repository: RegistrationRepository,
        competition_repository: CompetitionRepository
    ):
        self.registration_repository = registration_repository
        self.competition_repository = competition_repository

    async def execute(self, participant_id: UUID) -> List[RegistrationWithCompetition]:
        """Get all registrations for a participant.

        Args:
            participant_id: Participant ID

        Returns:
            List of registrations with competition info
        """
        # This would need a custom repository method
        # For now, we'll return empty list
        # TODO: Implement get_by_participant in RegistrationRepository
        return []
