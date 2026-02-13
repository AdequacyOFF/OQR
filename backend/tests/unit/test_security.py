"""Unit tests for security utilities."""

import pytest
from olimpqr.infrastructure.security import hash_password, verify_password


class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password("testpassword")
        assert hashed != "testpassword"
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        hashed = hash_password("correct")
        assert verify_password("correct", hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_verify_empty_password(self):
        assert verify_password("", "hash") is False
        assert verify_password("pass", "") is False

    def test_hash_empty_password_rejected(self):
        with pytest.raises(ValueError):
            hash_password("")

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # bcrypt uses random salt
