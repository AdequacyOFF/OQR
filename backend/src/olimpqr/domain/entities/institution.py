"""Institution entity."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class Institution:
    """Institution entity - school or educational organization.

    Attributes:
        id: Unique identifier
        name: Full institution name (unique)
        short_name: Short/abbreviated name
        city: City where the institution is located
        created_at: When institution was created
    """
    name: str
    id: UUID = field(default_factory=uuid4)
    short_name: str | None = None
    city: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Название учреждения должно быть не менее 2 символов")
