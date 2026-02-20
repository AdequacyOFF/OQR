"""List institutions use case."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.entities import Institution
from ....domain.repositories import InstitutionRepository


@dataclass
class InstitutionItem:
    id: UUID
    name: str
    short_name: str | None
    city: str | None


class ListInstitutionsUseCase:
    """List all institutions with pagination."""

    def __init__(self, institution_repository: InstitutionRepository):
        self.institution_repo = institution_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> list[InstitutionItem]:
        institutions = await self.institution_repo.get_all(skip=skip, limit=limit)
        return [
            InstitutionItem(
                id=i.id, name=i.name, short_name=i.short_name, city=i.city
            )
            for i in institutions
        ]
