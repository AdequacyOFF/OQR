"""Rate limiting configuration using slowapi."""

from slowapi import Limiter
from slowapi.util import get_remote_address


# Rate limiter instance
# Default: 100 requests per minute per IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    headers_enabled=True,  # Add X-RateLimit headers to responses
)
