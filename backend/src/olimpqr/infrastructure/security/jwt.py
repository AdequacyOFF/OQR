"""JWT token utilities."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from dataclasses import dataclass

import jwt
from jwt.exceptions import InvalidTokenError

from ...config import settings
from ...domain.value_objects import UserRole


@dataclass
class JWTPayload:
    """JWT token payload."""
    user_id: UUID
    email: str
    role: UserRole
    exp: datetime


def create_access_token(
    user_id: UUID,
    email: str,
    role: UserRole,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID
        email: User email
        role: User role
        expires_delta: Token expiration time (defaults to settings.jwt_expire_minutes)

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)

    expire = datetime.utcnow() + expires_delta

    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role.value,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_access_token(token: str) -> JWTPayload:
    """Verify and decode JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded JWT payload

    Raises:
        InvalidTokenError: If token is invalid or expired
        ValueError: If token payload is malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = UUID(payload.get("sub"))
        email = payload.get("email")
        role = UserRole(payload.get("role"))
        exp = datetime.fromtimestamp(payload.get("exp"))

        if not email:
            raise ValueError("Email не найден в токене")

        return JWTPayload(
            user_id=user_id,
            email=email,
            role=role,
            exp=exp
        )

    except InvalidTokenError as e:
        raise InvalidTokenError(f"Неверный токен: {str(e)}")
    except (KeyError, ValueError, TypeError) as e:
        raise ValueError(f"Некорректные данные токена: {str(e)}")
