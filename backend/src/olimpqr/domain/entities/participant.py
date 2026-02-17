"""Participant entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Participant:
    """Participant entity - extends User with participant-specific data.

    Attributes:
        id: Unique identifier
        user_id: Reference to User entity
        full_name: Participant's full name (shown in results)
        school: School name
        grade: School grade (e.g., 9, 10, 11)
        created_at: When participant profile was created
        updated_at: When participant profile was last updated
    """
    user_id: UUID
    full_name: str
    school: str
    grade: int
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.full_name or len(self.full_name.strip()) < 2:
            raise ValueError("ФИО должно быть не менее 2 символов")
        if not self.school or len(self.school.strip()) < 2:
            raise ValueError("Название школы должно быть не менее 2 символов")
        if not (1 <= self.grade <= 12):
            raise ValueError("Класс должен быть от 1 до 12")

    def update_profile(self, full_name: str | None = None, school: str | None = None, grade: int | None = None):
        """Update participant profile."""
        if full_name is not None:
            if len(full_name.strip()) < 2:
                raise ValueError("ФИО должно быть не менее 2 символов")
            self.full_name = full_name

        if school is not None:
            if len(school.strip()) < 2:
                raise ValueError("Название школы должно быть не менее 2 символов")
            self.school = school

        if grade is not None:
            if not (1 <= grade <= 12):
                raise ValueError("Класс должен быть от 1 до 12")
            self.grade = grade

        self.updated_at = datetime.utcnow()
