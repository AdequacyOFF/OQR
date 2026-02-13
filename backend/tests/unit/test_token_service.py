"""Unit tests for TokenService."""

import pytest
from olimpqr.domain.services import TokenService
from olimpqr.domain.value_objects import Token, TokenHash


class TestTokenService:
    """Test cases for TokenService."""

    @pytest.fixture
    def token_service(self):
        """Create TokenService instance for testing."""
        return TokenService(secret_key="test-secret-key-at-least-32-characters-long")

    def test_generate_token_creates_valid_token(self, token_service):
        """Test that generate_token creates a valid token with hash."""
        token = token_service.generate_token()

        assert isinstance(token, Token)
        assert isinstance(token.hash, TokenHash)
        assert len(token.raw) > 0
        assert len(token.hash.value) == 64  # SHA256 hex digest length

    def test_generate_token_creates_unique_tokens(self, token_service):
        """Test that generate_token creates unique tokens."""
        token1 = token_service.generate_token()
        token2 = token_service.generate_token()

        assert token1.raw != token2.raw
        assert token1.hash.value != token2.hash.value

    def test_verify_token_accepts_valid_token(self, token_service):
        """Test that verify_token accepts valid tokens."""
        token = token_service.generate_token()

        result = token_service.verify_token(token.raw, token.hash.value)

        assert result is True

    def test_verify_token_rejects_invalid_token(self, token_service):
        """Test that verify_token rejects invalid tokens."""
        token = token_service.generate_token()
        wrong_raw = "wrong-token-value"

        result = token_service.verify_token(wrong_raw, token.hash.value)

        assert result is False

    def test_verify_token_rejects_empty_values(self, token_service):
        """Test that verify_token rejects empty values."""
        assert token_service.verify_token("", "hash") is False
        assert token_service.verify_token("token", "") is False

    def test_hash_token_produces_consistent_hash(self, token_service):
        """Test that hash_token produces consistent hashes."""
        raw_token = "test-token-value"

        hash1 = token_service.hash_token(raw_token)
        hash2 = token_service.hash_token(raw_token)

        assert hash1.value == hash2.value

    def test_different_secret_keys_produce_different_hashes(self):
        """Test that different secret keys produce different hashes."""
        raw_token = "test-token-value"

        service1 = TokenService("secret-key-1-must-be-at-least-32-chars")
        service2 = TokenService("secret-key-2-must-be-at-least-32-chars")

        hash1 = service1.hash_token(raw_token)
        hash2 = service2.hash_token(raw_token)

        assert hash1.value != hash2.value

    def test_token_service_requires_long_secret_key(self):
        """Test that TokenService requires secret key of at least 32 characters."""
        with pytest.raises(ValueError, match="Secret key must be at least 32 characters"):
            TokenService("short")

    def test_generate_token_custom_size(self, token_service):
        """Test that generate_token respects custom size parameter."""
        token = token_service.generate_token(size_bytes=64)  # 512 bits

        # URL-safe base64 encoding: 4 chars per 3 bytes
        expected_min_length = (64 * 4) // 3
        assert len(token.raw) >= expected_min_length
