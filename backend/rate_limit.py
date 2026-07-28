import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from config import settings

_attempts: dict[str, deque] = defaultdict(deque)


def enforce_rate_limit(request: Request, bucket: str) -> None:
    """Simple in-memory sliding-window limiter, keyed by client IP + bucket name.

    Not shared across processes/workers — fine for a single-instance deployment,
    swap for a Redis-backed limiter before scaling out horizontally.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"{bucket}:{client_ip}"
    window = settings.login_rate_limit_window_seconds
    limit = settings.login_rate_limit_attempts

    now = time.monotonic()
    attempts = _attempts[key]
    while attempts and now - attempts[0] > window:
        attempts.popleft()

    if len(attempts) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many attempts. Please wait a moment and try again.",
        )

    attempts.append(now)
