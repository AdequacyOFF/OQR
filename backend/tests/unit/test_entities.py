"""Unit tests for domain entities."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from olimpqr.domain.entities import (
    User, Participant, Competition, Registration, EntryToken, Attempt, Scan, AuditLog,
)
from olimpqr.domain.value_objects import (
    UserRole, CompetitionStatus, RegistrationStatus, AttemptStatus, TokenHash,
)


# --- User ---

class TestUser:
    def test_create_valid_user(self):
        u = User(email="a@b.com", password_hash="hashed", role=UserRole.PARTICIPANT)
        assert u.is_active is True
        assert u.role == UserRole.PARTICIPANT

    def test_user_invalid_email(self):
        with pytest.raises(ValueError):
            User(email="bad", password_hash="h", role=UserRole.PARTICIPANT)

    def test_deactivate_activate(self):
        u = User(email="a@b.com", password_hash="h", role=UserRole.ADMIN)
        u.deactivate()
        assert u.is_active is False
        u.activate()
        assert u.is_active is True


# --- Competition ---

class TestCompetition:
    def _make(self, **kw):
        defaults = dict(
            name="Math Olympiad",
            date=datetime.utcnow().date(),
            registration_start=datetime.utcnow(),
            registration_end=datetime.utcnow() + timedelta(days=7),
            variants_count=4,
            max_score=100,
            created_by=uuid4(),
        )
        defaults.update(kw)
        return Competition(**defaults)

    def test_create_valid(self):
        c = self._make()
        assert c.status == CompetitionStatus.DRAFT

    def test_status_transitions(self):
        c = self._make()
        c.open_registration()
        assert c.status == CompetitionStatus.REGISTRATION_OPEN

        c.start_competition()
        assert c.status == CompetitionStatus.IN_PROGRESS

        c.start_checking()
        assert c.status == CompetitionStatus.CHECKING

        c.publish_results()
        assert c.status == CompetitionStatus.PUBLISHED

    def test_invalid_transition(self):
        c = self._make()
        with pytest.raises(ValueError):
            c.start_competition()  # Cannot go DRAFT -> IN_PROGRESS

    def test_registration_dates_order(self):
        with pytest.raises(ValueError):
            self._make(
                registration_start=datetime.utcnow() + timedelta(days=7),
                registration_end=datetime.utcnow(),
            )


# --- Registration ---

class TestRegistration:
    def test_lifecycle(self):
        r = Registration(participant_id=uuid4(), competition_id=uuid4())
        assert r.status == RegistrationStatus.PENDING

        r.admit()
        assert r.status == RegistrationStatus.ADMITTED
        assert r.can_generate_sheet is True

        r.complete()
        assert r.status == RegistrationStatus.COMPLETED

    def test_cannot_admit_twice(self):
        r = Registration(participant_id=uuid4(), competition_id=uuid4())
        r.admit()
        with pytest.raises(ValueError):
            r.admit()

    def test_cancel(self):
        r = Registration(participant_id=uuid4(), competition_id=uuid4())
        r.cancel()
        assert r.is_active is False


# --- EntryToken ---

class TestEntryToken:
    def _hash(self):
        return TokenHash(value="a" * 64)

    def test_create_valid(self):
        et = EntryToken.create(
            token_hash=self._hash(),
            registration_id=uuid4(),
            expire_hours=24,
        )
        assert et.is_valid is True
        assert et.is_expired is False
        assert et.is_used is False

    def test_use_token(self):
        et = EntryToken.create(token_hash=self._hash(), registration_id=uuid4())
        et.use()
        assert et.is_used is True
        assert et.is_valid is False

    def test_cannot_use_twice(self):
        et = EntryToken.create(token_hash=self._hash(), registration_id=uuid4())
        et.use()
        with pytest.raises(ValueError, match="already been used"):
            et.use()

    def test_expired_token(self):
        et = EntryToken(
            token_hash=self._hash(),
            registration_id=uuid4(),
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        assert et.is_expired is True
        assert et.is_valid is False

    def test_cannot_use_expired(self):
        et = EntryToken(
            token_hash=self._hash(),
            registration_id=uuid4(),
            expires_at=datetime.utcnow() - timedelta(hours=1),
        )
        with pytest.raises(ValueError, match="expired"):
            et.use()


# --- Attempt ---

class TestAttempt:
    def _make(self):
        return Attempt(
            registration_id=uuid4(),
            variant_number=1,
            sheet_token_hash=TokenHash(value="b" * 64),
        )

    def test_create_valid(self):
        a = self._make()
        assert a.status == AttemptStatus.PRINTED
        assert a.score_total is None

    def test_score_lifecycle(self):
        a = self._make()
        a.mark_scanned()
        assert a.status == AttemptStatus.SCANNED

        a.apply_score(85, confidence=0.95)
        assert a.status == AttemptStatus.SCORED
        assert a.score_total == 85

        a.publish()
        assert a.status == AttemptStatus.PUBLISHED

    def test_invalidate(self):
        a = self._make()
        a.invalidate()
        assert a.status == AttemptStatus.INVALIDATED
        assert a.is_valid is False

    def test_negative_score_rejected(self):
        a = self._make()
        a.mark_scanned()
        with pytest.raises(ValueError):
            a.apply_score(-1)


# --- Scan ---

class TestScan:
    def test_update_ocr(self):
        s = Scan(attempt_id=uuid4(), file_path="scans/1.png", uploaded_by=uuid4())
        s.update_ocr_result(score=72, confidence=0.88, raw_text="72")
        assert s.is_processed
        assert s.has_valid_score

    def test_verify(self):
        s = Scan(attempt_id=uuid4(), file_path="scans/1.png", uploaded_by=uuid4())
        s.update_ocr_result(score=72, confidence=0.88, raw_text="72")
        verifier = uuid4()
        s.verify(verified_by=verifier, corrected_score=75)
        assert s.is_verified
        assert s.ocr_score == 75


# --- AuditLog ---

class TestAuditLog:
    def test_create_log(self):
        log = AuditLog.create_log(
            entity_type="registration",
            entity_id=uuid4(),
            action="admitted",
            user_id=uuid4(),
            ip_address="127.0.0.1",
            variant=3,
        )
        assert log.details["variant"] == 3
        assert log.entity_type == "registration"
