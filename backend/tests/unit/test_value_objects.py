"""Unit tests for value objects."""

import pytest
from olimpqr.domain.value_objects import (
    Token, TokenHash, Score, UserRole,
    CompetitionStatus, RegistrationStatus, AttemptStatus,
)


class TestTokenHash:
    def test_valid_hash(self):
        th = TokenHash(value="a" * 64)
        assert len(th.value) == 64

    def test_empty_hash_rejected(self):
        with pytest.raises(ValueError):
            TokenHash(value="")

    def test_wrong_length_rejected(self):
        with pytest.raises(ValueError):
            TokenHash(value="abc")

    def test_immutable(self):
        th = TokenHash(value="a" * 64)
        with pytest.raises(AttributeError):
            th.value = "b" * 64


class TestToken:
    def test_valid_token(self):
        t = Token(raw="raw123", hash=TokenHash(value="a" * 64))
        assert t.raw == "raw123"

    def test_empty_raw_rejected(self):
        with pytest.raises(ValueError):
            Token(raw="", hash=TokenHash(value="a" * 64))


class TestScore:
    def test_valid_score(self):
        s = Score(value=85, max_value=100, confidence=0.95)
        assert s.percentage == 85.0

    def test_negative_rejected(self):
        with pytest.raises(ValueError):
            Score(value=-1, max_value=100)

    def test_exceeds_max_rejected(self):
        with pytest.raises(ValueError):
            Score(value=101, max_value=100)

    def test_bad_confidence_rejected(self):
        with pytest.raises(ValueError):
            Score(value=50, max_value=100, confidence=1.5)


class TestUserRole:
    def test_staff_roles(self):
        assert UserRole.ADMIN.is_staff is True
        assert UserRole.ADMITTER.is_staff is True
        assert UserRole.SCANNER.is_staff is True
        assert UserRole.PARTICIPANT.is_staff is False

    def test_is_admin(self):
        assert UserRole.ADMIN.is_admin is True
        assert UserRole.PARTICIPANT.is_admin is False


class TestCompetitionStatus:
    def test_allows_registration(self):
        assert CompetitionStatus.REGISTRATION_OPEN.allows_registration is True
        assert CompetitionStatus.DRAFT.allows_registration is False

    def test_allows_admission(self):
        assert CompetitionStatus.IN_PROGRESS.allows_admission is True
        assert CompetitionStatus.CHECKING.allows_admission is False

    def test_results_visible(self):
        assert CompetitionStatus.PUBLISHED.results_visible is True
        assert CompetitionStatus.CHECKING.results_visible is False


class TestAttemptStatus:
    def test_can_apply_score(self):
        assert AttemptStatus.SCANNED.can_apply_score is True
        assert AttemptStatus.SCORED.can_apply_score is True
        assert AttemptStatus.PRINTED.can_apply_score is False

    def test_has_score(self):
        assert AttemptStatus.SCORED.has_score is True
        assert AttemptStatus.PUBLISHED.has_score is True
        assert AttemptStatus.SCANNED.has_score is False
