"""Token service for secure token generation and verification.

This is the core security component. It ensures:
1. Tokens have 256 bits of cryptographic entropy
2. Only HMAC-SHA256 hashes are stored in the database
3. Token verification uses constant-time comparison (timing attack protection)
4. Raw tokens are never stored, only returned at generation time
"""

import hmac
import hashlib
import secrets

from ..value_objects import Token, TokenHash


class TokenService:
    """Service for generating and verifying cryptographically secure tokens.

    Tokens are used for:
    - Entry QR codes (one-time admission)
    - Answer sheet QR codes (linking scans to attempts)

    Security properties:
    - 256 bits of entropy (impossible to guess)
    - HMAC-SHA256 hashing with secret key
    - Constant-time comparison for timing attack resistance
    """

    def __init__(self, secret_key: str):
        """Initialize token service.

        Args:
            secret_key: Secret key for HMAC (should be different from JWT secret)
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters")
        self.secret_key = secret_key.encode('utf-8')

    def generate_token(self, size_bytes: int = 32) -> Token:
        """Generate a new cryptographically secure token with HMAC hash.

        Args:
            size_bytes: Size of token in bytes (default 32 = 256 bits)

        Returns:
            Token object with raw value and hash

        Note:
            The raw value should only be embedded in QR codes.
            Only the hash should be stored in the database.
        """
        # Generate token with cryptographic random number generator
        raw_token = secrets.token_urlsafe(size_bytes)

        # Compute HMAC-SHA256 hash
        token_hash = self._compute_hash(raw_token)

        return Token(raw=raw_token, hash=token_hash)

    def verify_token(self, raw_token: str, stored_hash: str) -> bool:
        """Verify a token against its stored hash.

        Args:
            raw_token: Raw token value (from QR code)
            stored_hash: HMAC hash stored in database

        Returns:
            True if token is valid, False otherwise

        Note:
            Uses constant-time comparison to prevent timing attacks.
        """
        if not raw_token or not stored_hash:
            return False

        # Compute hash of provided token
        computed_hash = self._compute_hash(raw_token)

        # Constant-time comparison (prevents timing attacks)
        return hmac.compare_digest(computed_hash.value, stored_hash)

    def hash_token(self, raw_token: str) -> TokenHash:
        """Compute HMAC-SHA256 hash of a token.

        Args:
            raw_token: Raw token value

        Returns:
            TokenHash object
        """
        return self._compute_hash(raw_token)

    def _compute_hash(self, raw_token: str) -> TokenHash:
        """Compute HMAC-SHA256 hash of a token.

        Args:
            raw_token: Raw token value

        Returns:
            TokenHash object with hex digest
        """
        # Compute HMAC-SHA256
        h = hmac.new(
            self.secret_key,
            raw_token.encode('utf-8'),
            hashlib.sha256
        )

        # Return hex digest (64 characters)
        return TokenHash(value=h.hexdigest())
