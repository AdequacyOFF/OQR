"""Answer sheet model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from olimpqr.domain.value_objects.sheet_kind import SheetKind

from ..base import Base

if TYPE_CHECKING:
    from .attempt import AttemptModel
    from .scan import ScanModel


class AnswerSheetModel(Base):
    """Answer sheet database model."""

    __tablename__ = "answer_sheets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    sheet_token_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True
    )
    kind: Mapped[SheetKind] = mapped_column(
        SQLEnum(
            SheetKind,
            name="sheetkind",
            native_enum=True,
            create_type=False,
            values_callable=lambda e: [member.value for member in e],
        ),
        nullable=False
    )
    pdf_file_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )

    # Relationships
    attempt: Mapped["AttemptModel"] = relationship(
        "AttemptModel",
        lazy="selectin"
    )
    scans: Mapped[list["ScanModel"]] = relationship(
        "ScanModel",
        back_populates="answer_sheet"
    )

    def __repr__(self) -> str:
        return f"<AnswerSheetModel(id={self.id}, attempt_id={self.attempt_id}, kind={self.kind})>"
