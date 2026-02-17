"""Entry token entity."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from ..value_objects import TokenHash


@dataclass
class EntryToken:
    """Entry token entity - for admission QR codes.

    The raw token is now stored to allow participants to retrieve their QR code.
    The token hash is used for verification.

    Attributes:
        id: Unique identifier
        token_hash: HMAC-SHA256 hash of the token
        raw_token: Raw token value (optional for backward compatibility)
        registration_id: Reference to Registration
        expires_at: When token expires
        used_at: When token was used (None if not used yet)
        created_at: When token was created
    """
    token_hash: TokenHash
    registration_id: UUID
    expires_at: datetime
    id: UUID = field(default_factory=uuid4)
    raw_token: str | None = None
    used_at: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not isinstance(self.token_hash, TokenHash):
            raise TypeError("token_hash must be a TokenHash instance")

    @classmethod
    def create(cls, token_hash: TokenHash, registration_id: UUID, expire_hours: int = 24) -> "EntryToken":
        """Create a new entry token with expiration time.

        Args:
            token_hash: HMAC hash of the token
            registration_id: Reference to registration
            expire_hours: Hours until token expires

        Returns:
            New EntryToken instance
        """
        expires_at = datetime.utcnow() + timedelta(hours=expire_hours)
        return cls(
            token_hash=token_hash,
            registration_id=registration_id,
            expires_at=expires_at
        )

    def use(self):
        """Mark token as used (one-time use)."""
        if self.used_at is not None:
            raise ValueError("Токен уже использован")
        if self.is_expired:
            raise ValueError("Срок действия токена истёк")
        self.used_at = datetime.utcnow()

    @property
    def is_expired(self) -> bool:
        """Check if token has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if token has been used."""
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired and not self.is_used
