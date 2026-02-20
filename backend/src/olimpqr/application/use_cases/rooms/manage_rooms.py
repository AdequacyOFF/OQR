"""Room management use cases."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.entities import Room
from ....domain.repositories import RoomRepository, CompetitionRepository


@dataclass
class RoomResult:
    id: UUID
    competition_id: UUID
    name: str
    capacity: int


class CreateRoomUseCase:
    """Create a room for a competition."""

    def __init__(self, room_repository: RoomRepository, competition_repository: CompetitionRepository):
        self.room_repo = room_repository
        self.competition_repo = competition_repository

    async def execute(self, competition_id: UUID, name: str, capacity: int) -> RoomResult:
        competition = await self.competition_repo.get_by_id(competition_id)
        if not competition:
            raise ValueError("Олимпиада не найдена")

        room = Room(competition_id=competition_id, name=name, capacity=capacity)
        await self.room_repo.create(room)

        return RoomResult(
            id=room.id,
            competition_id=room.competition_id,
            name=room.name,
            capacity=room.capacity,
        )


class ListRoomsUseCase:
    """List rooms for a competition."""

    def __init__(self, room_repository: RoomRepository):
        self.room_repo = room_repository

    async def execute(self, competition_id: UUID) -> list[RoomResult]:
        rooms = await self.room_repo.get_by_competition(competition_id)
        return [
            RoomResult(id=r.id, competition_id=r.competition_id, name=r.name, capacity=r.capacity)
            for r in rooms
        ]


class DeleteRoomUseCase:
    """Delete a room."""

    def __init__(self, room_repository: RoomRepository):
        self.room_repo = room_repository

    async def execute(self, room_id: UUID) -> bool:
        return await self.room_repo.delete(room_id)
