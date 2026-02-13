"""FastAPI dependencies."""

from .auth import get_current_user, require_role, get_current_active_user

__all__ = [
    "get_current_user",
    "require_role",
    "get_current_active_user",
]
