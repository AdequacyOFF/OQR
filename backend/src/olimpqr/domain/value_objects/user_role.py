"""User role enumeration."""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system.

    - PARTICIPANT: Can register for competitions and view their results
    - ADMITTER: Can verify entry QR codes and generate answer sheets
    - SCANNER: Can upload scans and verify OCR results
    - ADMIN: Full system access - manage users, competitions, publish results
    """
    PARTICIPANT = "participant"
    ADMITTER = "admitter"
    SCANNER = "scanner"
    ADMIN = "admin"
    INVIGILATOR = "invigilator"

    @property
    def is_staff(self) -> bool:
        """Check if role is staff (admitter, scanner, invigilator, or admin)."""
        return self in (UserRole.ADMITTER, UserRole.SCANNER, UserRole.INVIGILATOR, UserRole.ADMIN)

    @property
    def is_admin(self) -> bool:
        """Check if role is admin."""
        return self == UserRole.ADMIN
