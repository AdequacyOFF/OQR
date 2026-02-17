"""Competition entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from uuid import UUID, uuid4

from ..value_objects import CompetitionStatus


@dataclass
class Competition:
    """Competition entity.

    Attributes:
        id: Unique identifier
        name: Competition name
        date: Competition date
        registration_start: When registration opens
        registration_end: When registration closes
        variants_count: Number of test variants
        max_score: Maximum possible score
        status: Competition status
        created_by: User who created the competition
        created_at: When competition was created
        updated_at: When competition was last updated
    """
    name: str
    date: date
    registration_start: datetime
    registration_end: datetime
    variants_count: int
    max_score: int
    created_by: UUID
    id: UUID = field(default_factory=uuid4)
    status: CompetitionStatus = CompetitionStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 3:
            raise ValueError("Название олимпиады должно быть не менее 3 символов")
        if self.registration_start >= self.registration_end:
            raise ValueError("Начало регистрации должно быть раньше окончания")
        if self.variants_count < 1:
            raise ValueError("Должен быть хотя бы один вариант")
        if self.max_score < 1:
            raise ValueError("Максимальный балл должен быть положительным")

    def open_registration(self):
        """Open registration for participants."""
        if self.status != CompetitionStatus.DRAFT:
            raise ValueError("Открыть регистрацию можно только из статуса черновик")
        self.status = CompetitionStatus.REGISTRATION_OPEN
        self.updated_at = datetime.utcnow()

    def start_competition(self):
        """Start the competition (admission begins)."""
        if self.status != CompetitionStatus.REGISTRATION_OPEN:
            raise ValueError("Начать можно только из статуса открытая регистрация")
        self.status = CompetitionStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()

    def start_checking(self):
        """Move to checking phase (all submissions in, scoring begins)."""
        if self.status != CompetitionStatus.IN_PROGRESS:
            raise ValueError("Начать проверку можно только из статуса в процессе")
        self.status = CompetitionStatus.CHECKING
        self.updated_at = datetime.utcnow()

    def publish_results(self):
        """Publish competition results to participants."""
        if self.status != CompetitionStatus.CHECKING:
            raise ValueError("Опубликовать можно только из статуса проверка")
        self.status = CompetitionStatus.PUBLISHED
        self.updated_at = datetime.utcnow()

    @property
    def is_registration_open(self) -> bool:
        """Check if registration is currently open.

        Registration is open if the status is REGISTRATION_OPEN.
        The admin controls this status manually, so time-based checks
        are not enforced here.
        """
        return self.status == CompetitionStatus.REGISTRATION_OPEN

    @property
    def is_in_progress(self) -> bool:
        """Check if competition is in progress."""
        return self.status == CompetitionStatus.IN_PROGRESS

    @property
    def are_results_published(self) -> bool:
        """Check if results are published."""
        return self.status == CompetitionStatus.PUBLISHED
