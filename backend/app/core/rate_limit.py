"""Rate limiting configuration using slowapi.

Provides a shared limiter instance and a key function that
identifies clients by IP address (or X-Forwarded-For behind a proxy).
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request


def _get_client_ip(request: Request) -> str:
    """Extract the client IP, respecting X-Forwarded-For for Cloud Run."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=_get_client_ip)
