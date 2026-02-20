"""Scan model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .attempt import AttemptModel
    from .answer_sheet import AnswerSheetModel
    from .user import UserModel


class ScanModel(Base):
    """Scan database model."""

    __tablename__ = "scans"
    __table_args__ = (
        Index("ix_scans_attempt_created", "attempt_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    attempt_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("attempts.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    answer_sheet_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("answer_sheets.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    ocr_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )
    ocr_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    ocr_raw_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    attempt: Mapped[Optional["AttemptModel"]] = relationship(
        "AttemptModel",
        back_populates="scans",
        lazy="selectin"
    )
    answer_sheet: Mapped[Optional["AnswerSheetModel"]] = relationship(
        "AnswerSheetModel",
        back_populates="scans",
        lazy="selectin"
    )
    verifier: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="scans_verified",
        foreign_keys=[verified_by],
        lazy="selectin"
    )
    uploader: Mapped[Optional["UserModel"]] = relationship(
        "UserModel",
        back_populates="scans_uploaded",
        foreign_keys=[uploaded_by],
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ScanModel(id={self.id}, attempt_id={self.attempt_id}, ocr_score={self.ocr_score})>"
