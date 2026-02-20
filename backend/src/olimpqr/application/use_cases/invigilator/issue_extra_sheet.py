"""Issue extra answer sheet use case."""

from dataclasses import dataclass
from uuid import UUID, uuid4

from ....domain.entities import AnswerSheet
from ....domain.value_objects import SheetKind
from ....domain.repositories import AnswerSheetRepository, AttemptRepository
from ....domain.services import TokenService
from ....infrastructure.pdf import SheetGenerator
from ....infrastructure.storage import MinIOStorage
from ....config import settings


@dataclass
class IssueExtraSheetResult:
    answer_sheet_id: UUID
    sheet_token: str
    pdf_url: str


class IssueExtraSheetUseCase:
    """Issue an extra answer sheet for an attempt."""

    def __init__(
        self,
        answer_sheet_repository: AnswerSheetRepository,
        attempt_repository: AttemptRepository,
        token_service: TokenService,
        sheet_generator: SheetGenerator,
        storage: MinIOStorage,
    ):
        self.answer_sheet_repo = answer_sheet_repository
        self.attempt_repo = attempt_repository
        self.token_service = token_service
        self.sheet_generator = sheet_generator
        self.storage = storage

    async def execute(self, attempt_id: UUID) -> IssueExtraSheetResult:
        attempt = await self.attempt_repo.get_by_id(attempt_id)
        if not attempt:
            raise ValueError("Попытка не найдена")

        # Generate new sheet token
        sheet_token = self.token_service.generate_token(
            size_bytes=settings.qr_token_size_bytes
        )

        # Create answer sheet
        answer_sheet = AnswerSheet(
            id=uuid4(),
            attempt_id=attempt_id,
            sheet_token_hash=sheet_token.hash,
            kind=SheetKind.EXTRA,
        )

        # Generate PDF
        pdf_bytes = self.sheet_generator.generate_answer_sheet(
            competition_name="Extra Sheet",
            variant_number=attempt.variant_number,
            sheet_token=sheet_token.raw,
        )

        # Upload PDF
        object_name = f"sheets/extra/{attempt_id}/{answer_sheet.id}.pdf"
        self.storage.upload_file(
            bucket=settings.minio_bucket_sheets,
            object_name=object_name,
            data=pdf_bytes,
            content_type="application/pdf",
        )

        answer_sheet.pdf_file_path = object_name
        await self.answer_sheet_repo.create(answer_sheet)

        pdf_url = f"admission/sheets/{attempt_id}/download"

        return IssueExtraSheetResult(
            answer_sheet_id=answer_sheet.id,
            sheet_token=sheet_token.raw,
            pdf_url=pdf_url,
        )
