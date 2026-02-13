"""Verify entry QR code use case."""

from uuid import UUID
from dataclasses import dataclass

from ....domain.repositories import (
    EntryTokenRepository,
    RegistrationRepository,
    ParticipantRepository,
    CompetitionRepository,
)
from ....domain.services import TokenService


@dataclass
class VerifyEntryQRResult:
    """Result of entry QR verification."""
    registration_id: UUID
    participant_name: str
    participant_school: str
    participant_grade: int
    competition_name: str
    competition_id: UUID
    can_proceed: bool
    message: str


class VerifyEntryQRUseCase:
    """Verify an entry QR code scanned by an admitter.

    Checks:
    1. Compute HMAC hash of raw token
    2. Find entry_token by hash in DB
    3. Verify token not expired
    4. Verify token not already used
    5. Return participant + competition info for admitter confirmation
    """

    def __init__(
        self,
        token_service: TokenService,
        entry_token_repository: EntryTokenRepository,
        registration_repository: RegistrationRepository,
        participant_repository: ParticipantRepository,
        competition_repository: CompetitionRepository,
    ):
        self.token_service = token_service
        self.entry_token_repo = entry_token_repository
        self.registration_repo = registration_repository
        self.participant_repo = participant_repository
        self.competition_repo = competition_repository

    async def execute(self, raw_token: str) -> VerifyEntryQRResult:
        """Verify entry QR token.

        Args:
            raw_token: Raw token value scanned from QR code

        Returns:
            Verification result with participant and competition info

        Raises:
            ValueError: If token is invalid, expired, or already used
        """
        if not raw_token:
            raise ValueError("Token cannot be empty")

        # 1. Compute hash
        token_hash = self.token_service.hash_token(raw_token)

        # 2. Find entry token by hash
        entry_token = await self.entry_token_repo.get_by_token_hash(token_hash.value)
        if not entry_token:
            raise ValueError("Token not found")

        # 3. Check expiry
        if entry_token.is_expired:
            raise ValueError("Token has expired")

        # 4. Check if already used
        if entry_token.is_used:
            raise ValueError("Token has already been used")

        # 5. Get registration, participant, competition
        registration = await self.registration_repo.get_by_id(entry_token.registration_id)
        if not registration:
            raise ValueError("Registration not found")

        participant = await self.participant_repo.get_by_id(registration.participant_id)
        if not participant:
            raise ValueError("Participant not found")

        competition = await self.competition_repo.get_by_id(registration.competition_id)
        if not competition:
            raise ValueError("Competition not found")

        # 6. Check competition is in progress (admission allowed)
        if not competition.is_in_progress:
            return VerifyEntryQRResult(
                registration_id=registration.id,
                participant_name=participant.full_name,
                participant_school=participant.school,
                participant_grade=participant.grade,
                competition_name=competition.name,
                competition_id=competition.id,
                can_proceed=False,
                message=f"Competition is not in progress (status: {competition.status.value})",
            )

        return VerifyEntryQRResult(
            registration_id=registration.id,
            participant_name=participant.full_name,
            participant_school=participant.school,
            participant_grade=participant.grade,
            competition_name=competition.name,
            competition_id=competition.id,
            can_proceed=True,
            message="Participant verified. Proceed with admission.",
        )
