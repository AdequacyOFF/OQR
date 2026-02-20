"""Sheet kind enumeration for answer sheets."""

from enum import Enum


class SheetKind(str, Enum):
    """Kind of answer sheet."""
    PRIMARY = "primary"
    EXTRA = "extra"
