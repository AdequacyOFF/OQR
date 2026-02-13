"""Rate limiting configuration using slowapi."""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address


_enabled = os.environ.get("ENVIRONMENT", "development") != "test"

# Rate limiter instance
# Default: 100 requests per minute per IP
# Disabled in test environment
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    headers_enabled=True,  # Add X-RateLimit headers to responses
    enabled=_enabled,
)
