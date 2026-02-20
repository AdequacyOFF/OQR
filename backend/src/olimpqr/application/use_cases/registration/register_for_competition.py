"""Register for competition use case."""

from uuid import UUID, uuid4
from dataclasses import dataclass

from ....domain.entities import Registration, EntryToken
from ....domain.repositories import (
    RegistrationRepository,
    CompetitionRepository,
    ParticipantRepository,
    EntryTokenRepository
)
from ....domain.services import TokenService
from ....config import settings


@dataclass
class RegisterForCompetitionResult:
    """Result of registration."""
    registration_id: UUID
    entry_token: str  # Raw token for QR code


class RegisterForCompetitionUseCase:
    """Use case for registering participant for competition."""

    def __init__(
        self,
        registration_repository: RegistrationRepository,
        competition_repository: CompetitionRepository,
        participant_repository: ParticipantRepository,
        entry_token_repository: EntryTokenRepository,
        token_service: TokenService
    ):
        self.registration_repository = registration_repository
        self.competition_repository = competition_repository
        self.participant_repository = participant_repository
        self.entry_token_repository = entry_token_repository
        self.token_service = token_service

    async def execute(
        self,
        participant_id: UUID,
        competition_id: UUID,
        skip_status_check: bool = False,
    ) -> RegisterForCompetitionResult:
        """Register participant for competition.

        Args:
            participant_id: Participant ID
            competition_id: Competition ID

        Returns:
            Registration result with entry token

        Raises:
            ValueError: If validation fails
        """
        # Check participant exists
        participant = await self.participant_repository.get_by_id(participant_id)
        if not participant:
            raise ValueError("Участник не найден")

        # Check competition exists
        competition = await self.competition_repository.get_by_id(competition_id)
        if not competition:
            raise ValueError("Олимпиада не найдена")

        # Check registration is open
        if not skip_status_check and not competition.is_registration_open:
            raise ValueError("Регистрация на эту олимпиаду закрыта")

        # Check for duplicate registration
        existing = await self.registration_repository.get_by_participant_and_competition(
            participant_id, competition_id
        )
        if existing:
            raise ValueError("Вы уже зарегистрированы на эту олимпиаду")

        # Create registration
        registration = Registration(
            id=uuid4(),
            participant_id=participant_id,
            competition_id=competition_id
        )
        registration = await self.registration_repository.create(registration)

        # Generate entry token
        token = self.token_service.generate_token(
            size_bytes=settings.qr_token_size_bytes
        )

        # Create entry token entity
        entry_token = EntryToken.create(
            token_hash=token.hash,
            registration_id=registration.id,
            expire_hours=settings.entry_token_expire_hours
        )
        # Store raw token for later retrieval
        entry_token.raw_token = token.raw
        await self.entry_token_repository.create(entry_token)

        return RegisterForCompetitionResult(
            registration_id=registration.id,
            entry_token=token.raw
        )
