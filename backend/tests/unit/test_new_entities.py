"""Unit tests for new domain entities and value objects."""

import pytest
from datetime import datetime, date
from uuid import uuid4

from olimpqr.domain.entities import (
    Institution, Room, SeatAssignment, Document, ParticipantEvent, AnswerSheet, Participant,
)
from olimpqr.domain.value_objects import (
    UserRole, EventType, SheetKind, TokenHash,
)


# --- UserRole (updated) ---

class TestUserRoleInvigilator:
    def test_invigilator_exists(self):
        assert UserRole.INVIGILATOR.value == "invigilator"

    def test_invigilator_is_staff(self):
        assert UserRole.INVIGILATOR.is_staff is True

    def test_invigilator_is_not_admin(self):
        assert UserRole.INVIGILATOR.is_admin is False


# --- EventType ---

class TestEventType:
    def test_values(self):
        assert EventType.START_WORK.value == "start_work"
        assert EventType.SUBMIT.value == "submit"
        assert EventType.EXIT_ROOM.value == "exit_room"
        assert EventType.ENTER_ROOM.value == "enter_room"


# --- SheetKind ---

class TestSheetKind:
    def test_values(self):
        assert SheetKind.PRIMARY.value == "primary"
        assert SheetKind.EXTRA.value == "extra"


# --- Institution ---

class TestInstitution:
    def test_create_valid(self):
        inst = Institution(name="Test School")
        assert inst.name == "Test School"
        assert inst.short_name is None
        assert inst.city is None

    def test_create_with_all_fields(self):
        inst = Institution(name="School #1", short_name="S1", city="Moscow")
        assert inst.short_name == "S1"
        assert inst.city == "Moscow"

    def test_name_too_short(self):
        with pytest.raises(ValueError):
            Institution(name="A")

    def test_empty_name(self):
        with pytest.raises(ValueError):
            Institution(name="")


# --- Room ---

class TestRoom:
    def test_create_valid(self):
        r = Room(competition_id=uuid4(), name="Room 301", capacity=30)
        assert r.capacity == 30

    def test_empty_name(self):
        with pytest.raises(ValueError):
            Room(competition_id=uuid4(), name="", capacity=30)

    def test_zero_capacity(self):
        with pytest.raises(ValueError):
            Room(competition_id=uuid4(), name="R1", capacity=0)


# --- SeatAssignment ---

class TestSeatAssignment:
    def test_create_valid(self):
        sa = SeatAssignment(registration_id=uuid4(), room_id=uuid4(), seat_number=5, variant_number=2)
        assert sa.seat_number == 5
        assert sa.variant_number == 2

    def test_invalid_seat_number(self):
        with pytest.raises(ValueError):
            SeatAssignment(registration_id=uuid4(), room_id=uuid4(), seat_number=0, variant_number=1)

    def test_invalid_variant_number(self):
        with pytest.raises(ValueError):
            SeatAssignment(registration_id=uuid4(), room_id=uuid4(), seat_number=1, variant_number=0)


# --- Document ---

class TestDocument:
    def test_create_valid(self):
        d = Document(participant_id=uuid4(), file_path="docs/test.pdf", file_type="application/pdf")
        assert d.file_type == "application/pdf"

    def test_empty_file_path(self):
        with pytest.raises(ValueError):
            Document(participant_id=uuid4(), file_path="", file_type="pdf")

    def test_empty_file_type(self):
        with pytest.raises(ValueError):
            Document(participant_id=uuid4(), file_path="test.pdf", file_type="")


# --- ParticipantEvent ---

class TestParticipantEvent:
    def test_create_valid(self):
        e = ParticipantEvent(attempt_id=uuid4(), event_type=EventType.START_WORK, recorded_by=uuid4())
        assert e.event_type == EventType.START_WORK

    def test_invalid_event_type(self):
        with pytest.raises(TypeError):
            ParticipantEvent(attempt_id=uuid4(), event_type="invalid", recorded_by=uuid4())


# --- AnswerSheet ---

class TestAnswerSheet:
    def test_create_valid(self):
        token_hash = TokenHash(value="a" * 64)
        sheet = AnswerSheet(attempt_id=uuid4(), sheet_token_hash=token_hash, kind=SheetKind.PRIMARY)
        assert sheet.kind == SheetKind.PRIMARY
        assert sheet.pdf_file_path is None

    def test_invalid_token_hash(self):
        with pytest.raises(TypeError):
            AnswerSheet(attempt_id=uuid4(), sheet_token_hash="not_a_hash", kind=SheetKind.PRIMARY)

    def test_invalid_kind(self):
        token_hash = TokenHash(value="a" * 64)
        with pytest.raises(TypeError):
            AnswerSheet(attempt_id=uuid4(), sheet_token_hash=token_hash, kind="invalid")


# --- Participant (updated with new fields) ---

class TestParticipantUpdated:
    def test_create_with_institution_and_dob(self):
        p = Participant(
            user_id=uuid4(),
            full_name="Test Person",
            school="Test School",
            grade=10,
            institution_id=uuid4(),
            dob=date(2010, 5, 15),
        )
        assert p.institution_id is not None
        assert p.dob == date(2010, 5, 15)

    def test_create_without_new_fields(self):
        p = Participant(user_id=uuid4(), full_name="Test Person", school="Test School", grade=10)
        assert p.institution_id is None
        assert p.dob is None
