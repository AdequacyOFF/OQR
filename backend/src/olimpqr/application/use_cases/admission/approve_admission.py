"""Approve admission and generate answer sheet use case."""

import random
from uuid import UUID, uuid4
from dataclasses import dataclass

from ....domain.entities import Attempt, AuditLog
from ....domain.repositories import (
    EntryTokenRepository,
    RegistrationRepository,
    CompetitionRepository,
    AttemptRepository,
    AuditLogRepository,
)
from ....domain.services import TokenService
from ....infrastructure.pdf import SheetGenerator
from ....infrastructure.storage import MinIOStorage
from ....config import settings


@dataclass
class ApproveAdmissionResult:
    """Result of admission approval."""
    attempt_id: UUID
    variant_number: int
    pdf_url: str
    sheet_token: str  # raw token for QR code on sheet


class ApproveAdmissionUseCase:
    """Approve admission: mark entry token used, generate answer sheet.

    Steps:
    1. Mark entry token as used (one-time use)
    2. Update registration status to ADMITTED
    3. Assign random variant number
    4. Generate sheet token (for answer sheet QR)
    5. Create Attempt entity
    6. Generate PDF answer sheet with QR
    7. Upload PDF to MinIO
    8. Log action to audit log
    """

    def __init__(
        self,
        token_service: TokenService,
        entry_token_repository: EntryTokenRepository,
        registration_repository: RegistrationRepository,
        competition_repository: CompetitionRepository,
        attempt_repository: AttemptRepository,
        audit_log_repository: AuditLogRepository,
        storage: MinIOStorage,
        sheet_generator: SheetGenerator,
    ):
        self.token_service = token_service
        self.entry_token_repo = entry_token_repository
        self.registration_repo = registration_repository
        self.competition_repo = competition_repository
        self.attempt_repo = attempt_repository
        self.audit_log_repo = audit_log_repository
        self.storage = storage
        self.sheet_generator = sheet_generator

    async def execute(
        self,
        registration_id: UUID,
        raw_entry_token: str,
        admitter_user_id: UUID,
        ip_address: str | None = None,
    ) -> ApproveAdmissionResult:
        """Approve admission and generate answer sheet.

        Args:
            registration_id: Registration to approve
            raw_entry_token: Raw entry token for verification
            admitter_user_id: ID of the admitter performing admission
            ip_address: IP address of the request

        Returns:
            Admission result with PDF URL and sheet token

        Raises:
            ValueError: If validation fails
        """
        # 1. Verify token again (double-check)
        token_hash = self.token_service.hash_token(raw_entry_token)
        entry_token = await self.entry_token_repo.get_by_token_hash(token_hash.value)
        if not entry_token:
            raise ValueError("Токен не найден")
        if entry_token.is_used:
            raise ValueError("Токен уже использован")
        if entry_token.is_expired:
            raise ValueError("Срок действия токена истёк")
        if entry_token.registration_id != registration_id:
            raise ValueError("Токен не соответствует регистрации")

        # 2. Mark entry token as used
        entry_token.use()
        await self.entry_token_repo.update(entry_token)

        # 3. Update registration status
        registration = await self.registration_repo.get_by_id(registration_id)
        if not registration:
            raise ValueError("Регистрация не найдена")
        registration.admit()
        await self.registration_repo.update(registration)

        # 4. Get competition for variant count
        competition = await self.competition_repo.get_by_id(registration.competition_id)
        if not competition:
            raise ValueError("Олимпиада не найдена")

        # 5. Assign random variant
        variant_number = random.randint(1, competition.variants_count)

        # 6. Generate sheet token
        sheet_token = self.token_service.generate_token(
            size_bytes=settings.qr_token_size_bytes
        )

        # 7. Create attempt
        attempt = Attempt(
            id=uuid4(),
            registration_id=registration_id,
            variant_number=variant_number,
            sheet_token_hash=sheet_token.hash,
        )

        # 8. Generate PDF
        pdf_bytes = self.sheet_generator.generate_answer_sheet(
            competition_name=competition.name,
            variant_number=variant_number,
            sheet_token=sheet_token.raw,
        )

        # 9. Upload PDF to MinIO
        object_name = f"sheets/{competition.id}/{attempt.id}.pdf"
        self.storage.upload_file(
            bucket=settings.minio_bucket_sheets,
            object_name=object_name,
            data=pdf_bytes,
            content_type="application/pdf",
        )

        # 10. Save attempt with file path
        attempt.pdf_file_path = object_name
        await self.attempt_repo.create(attempt)

        # 11. Mark registration as completed (sheet given)
        registration.complete()
        await self.registration_repo.update(registration)

        # 12. Audit log
        audit = AuditLog.create_log(
            entity_type="registration",
            entity_id=registration_id,
            action="admitted",
            user_id=admitter_user_id,
            ip_address=ip_address,
            variant_number=variant_number,
            attempt_id=str(attempt.id),
        )
        await self.audit_log_repo.create(audit)

        # 13. Generate backend download URL instead of presigned MinIO URL
        # This avoids signature mismatch issues when MinIO is accessed via different endpoints
        # Path is relative to API baseURL (/api/v1), so don't include the prefix
        pdf_url = f"admission/sheets/{attempt.id}/download"

        return ApproveAdmissionResult(
            attempt_id=attempt.id,
            variant_number=variant_number,
            pdf_url=pdf_url,
            sheet_token=sheet_token.raw,
        )
