"""Assign seat use case - core seating algorithm."""

from dataclasses import dataclass
from uuid import UUID

from ....domain.entities import SeatAssignment
from ....domain.repositories import (
    RoomRepository,
    SeatAssignmentRepository,
    RegistrationRepository,
    ParticipantRepository,
)


@dataclass
class AssignSeatResult:
    seat_assignment_id: UUID
    room_id: UUID
    room_name: str
    seat_number: int
    variant_number: int


class AssignSeatUseCase:
    """Assign a seat to a participant for a competition.

    Algorithm:
    1. Check if seat already assigned (idempotent)
    2. Get participant's institution_id
    3. Get all rooms for competition
    4. For each room, count same-institution occupants
    5. Pick room with fewest same-institution participants (tie-break: most free seats)
    6. Find next available seat number
    7. Assign variant: (seat_number % variants_count) + 1
    """

    def __init__(
        self,
        room_repository: RoomRepository,
        seat_assignment_repository: SeatAssignmentRepository,
        registration_repository: RegistrationRepository,
        participant_repository: ParticipantRepository,
    ):
        self.room_repo = room_repository
        self.seat_repo = seat_assignment_repository
        self.registration_repo = registration_repository
        self.participant_repo = participant_repository

    async def execute(
        self, registration_id: UUID, competition_id: UUID, variants_count: int
    ) -> AssignSeatResult | None:
        # 1. Check if already assigned (idempotent)
        existing = await self.seat_repo.get_by_registration(registration_id)
        if existing:
            room = await self.room_repo.get_by_id(existing.room_id)
            return AssignSeatResult(
                seat_assignment_id=existing.id,
                room_id=existing.room_id,
                room_name=room.name if room else "?",
                seat_number=existing.seat_number,
                variant_number=existing.variant_number,
            )

        # 2. Get rooms for competition
        rooms = await self.room_repo.get_by_competition(competition_id)
        if not rooms:
            return None  # No rooms configured, skip seating

        # 3. Get participant's institution
        registration = await self.registration_repo.get_by_id(registration_id)
        if not registration:
            raise ValueError("Регистрация не найдена")

        participant = await self.participant_repo.get_by_id(registration.participant_id)
        if not participant:
            raise ValueError("Участник не найден")

        institution_id = participant.institution_id

        # 4. Evaluate each room
        best_room = None
        best_same_inst = float('inf')
        best_free_seats = -1

        for room in rooms:
            occupied = await self.seat_repo.count_by_room(room.id)
            free_seats = room.capacity - occupied

            if free_seats <= 0:
                continue  # Room full

            if institution_id:
                same_inst = await self.seat_repo.count_by_room_and_institution(
                    room.id, institution_id
                )
            else:
                same_inst = 0

            # Pick room with fewest same-institution (tie-break: most free seats)
            if (same_inst < best_same_inst) or (
                same_inst == best_same_inst and free_seats > best_free_seats
            ):
                best_room = room
                best_same_inst = same_inst
                best_free_seats = free_seats

        if not best_room:
            raise ValueError("Нет свободных мест ни в одной аудитории")

        # 5. Find next available seat number
        room_assignments = await self.seat_repo.get_by_room(best_room.id)
        taken_seats = {a.seat_number for a in room_assignments}
        seat_number = 1
        while seat_number in taken_seats:
            seat_number += 1

        # 6. Assign variant
        variant_number = (seat_number % variants_count) + 1

        # 7. Create assignment
        assignment = SeatAssignment(
            registration_id=registration_id,
            room_id=best_room.id,
            seat_number=seat_number,
            variant_number=variant_number,
        )
        await self.seat_repo.create(assignment)

        return AssignSeatResult(
            seat_assignment_id=assignment.id,
            room_id=best_room.id,
            room_name=best_room.name,
            seat_number=seat_number,
            variant_number=variant_number,
        )
