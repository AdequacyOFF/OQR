"""Search institutions use case."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.repositories import InstitutionRepository


@dataclass
class InstitutionSearchItem:
    id: UUID
    name: str
    short_name: str | None
    city: str | None


class SearchInstitutionsUseCase:
    """Search institutions by name."""

    def __init__(self, institution_repository: InstitutionRepository):
        self.institution_repo = institution_repository

    async def execute(self, query: str, limit: int = 20) -> list[InstitutionSearchItem]:
        if not query or len(query.strip()) < 1:
            return []

        institutions = await self.institution_repo.search(query=query, limit=limit)
        return [
            InstitutionSearchItem(
                id=i.id, name=i.name, short_name=i.short_name, city=i.city
            )
            for i in institutions
        ]
