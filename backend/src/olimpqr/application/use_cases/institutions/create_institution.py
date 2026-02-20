"""Create institution use case."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.entities import Institution
from ....domain.repositories import InstitutionRepository


@dataclass
class CreateInstitutionResult:
    id: UUID
    name: str
    short_name: str | None
    city: str | None


class CreateInstitutionUseCase:
    """Create a new institution."""

    def __init__(self, institution_repository: InstitutionRepository):
        self.institution_repo = institution_repository

    async def execute(
        self, name: str, short_name: str | None = None, city: str | None = None
    ) -> CreateInstitutionResult:
        existing = await self.institution_repo.get_by_name(name)
        if existing:
            raise ValueError("Учреждение с таким названием уже существует")

        institution = Institution(name=name, short_name=short_name, city=city)
        await self.institution_repo.create(institution)

        return CreateInstitutionResult(
            id=institution.id,
            name=institution.name,
            short_name=institution.short_name,
            city=institution.city,
        )
