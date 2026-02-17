"""Get entry QR code use case."""

from uuid import UUID
from dataclasses import dataclass
from datetime import datetime

from ....domain.repositories import (
    RegistrationRepository,
    EntryTokenRepository,
    ParticipantRepository
)
from ....domain.services import QRService


@dataclass
class EntryQRResult:
    """Result with QR code data."""
    qr_code_base64: str
    expires_at: datetime
    is_used: bool


class GetEntryQRUseCase:
    """Use case for getting entry QR code."""

    def __init__(
        self,
        registration_repository: RegistrationRepository,
        entry_token_repository: EntryTokenRepository,
        participant_repository: ParticipantRepository,
        qr_service: QRService
    ):
        self.registration_repository = registration_repository
        self.entry_token_repository = entry_token_repository
        self.participant_repository = participant_repository
        self.qr_service = qr_service

    async def execute(
        self,
        registration_id: UUID,
        user_id: UUID
    ) -> EntryQRResult:
        """Get entry QR code for registration.

        Args:
            registration_id: Registration ID
            user_id: Current user ID (for ownership verification)

        Returns:
            QR code data

        Raises:
            ValueError: If validation fails
        """
        # Get registration
        registration = await self.registration_repository.get_by_id(registration_id)
        if not registration:
            raise ValueError("Регистрация не найдена")

        # Get participant
        participant = await self.participant_repository.get_by_id(registration.participant_id)
        if not participant:
            raise ValueError("Участник не найден")

        # Verify ownership
        if participant.user_id != user_id:
            raise ValueError("Доступ запрещён: это не ваша регистрация")

        # Get entry token
        entry_token = await self.entry_token_repository.get_by_registration(registration_id)
        if not entry_token:
            raise ValueError("Токен допуска не найден")

        # Note: We don't expose the raw token from DB (it's not stored)
        # The QR code was already generated during registration
        # This endpoint should return error - token can only be retrieved once during registration
        
        # For now, raise error - in production, token should be stored temporarily or returned only once
        raise ValueError("Токен допуска можно получить только во время регистрации. Обратитесь к администратору.")
