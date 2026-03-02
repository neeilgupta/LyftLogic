"""
FastAPI dependencies shared across routes.
"""
import time
from collections import defaultdict
from fastapi import HTTPException, Request

_WINDOW_SECONDS = 10 * 60  # 10 minutes
_IP_LIMIT = 5
_EMAIL_LIMIT = 3

_ip_times: dict[str, list[float]] = defaultdict(list)
_email_times: dict[str, list[float]] = defaultdict(list)


def _prune(timestamps: list[float], now: float) -> None:
    cutoff = now - _WINDOW_SECONDS
    timestamps[:] = [t for t in timestamps if t >= cutoff]


async def otp_rate_limit(request: Request) -> None:
    """Sliding-window rate limiter for POST /auth/request-code.

    Enforces:
      - 5 requests per IP per 10 minutes
      - 3 requests per email per 10 minutes

    IP is read from request.client.host only (no X-Forwarded-For).
    Email is extracted from the JSON request body.
    """
    now = time.monotonic()
    ip = (request.client.host or "") if request.client else ""

    _prune(_ip_times[ip], now)
    if len(_ip_times[ip]) >= _IP_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    # Count this attempt against the IP budget now, before the email check.
    # This ensures email-limited requests still consume IP slots — otherwise
    # cycling through email addresses bypasses the IP limit entirely.
    _ip_times[ip].append(now)

    try:
        body = await request.json()
        email = (body.get("email") or "").strip().lower()
    except Exception:
        email = ""

    if email:
        _prune(_email_times[email], now)
        if len(_email_times[email]) >= _EMAIL_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Too many requests for this email. Try again later.",
            )
        _email_times[email].append(now)
