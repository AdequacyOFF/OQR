"""Token value objects for secure QR code generation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenHash:
    """HMAC-SHA256 hash of a token.

    This is what gets stored in the database. The original token is never stored.
    """
    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Token hash cannot be empty")
        if len(self.value) != 64:  # SHA256 hex digest length
            raise ValueError("Invalid token hash length")


@dataclass(frozen=True)
class Token:
    """Token with both raw value and hash.

    The raw value is only available at generation time and is embedded in QR codes.
    Only the hash is stored in the database for security.
    """
    raw: str
    hash: TokenHash

    def __post_init__(self):
        if not self.raw:
            raise ValueError("Token raw value cannot be empty")
        if not isinstance(self.hash, TokenHash):
            raise TypeError("hash must be a TokenHash instance")
