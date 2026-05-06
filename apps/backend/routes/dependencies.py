"""
FastAPI dependencies shared across routes.
"""
import os
import time
from collections import defaultdict
from fastapi import HTTPException, Request

_WINDOW_SECONDS = 10 * 60  # 10 minutes
_PROD_IP_LIMIT = 5
_PROD_EMAIL_LIMIT = 3
_DEV_IP_LIMIT = 30
_DEV_EMAIL_LIMIT = 15

_ip_times: dict[str, list[float]] = defaultdict(list)
_email_times: dict[str, list[float]] = defaultdict(list)


def _prune(timestamps: list[float], now: float) -> None:
    cutoff = now - _WINDOW_SECONDS
    timestamps[:] = [t for t in timestamps if t >= cutoff]


def _limits() -> tuple[int, int]:
    if os.getenv("ENV") == "production":
        return _PROD_IP_LIMIT, _PROD_EMAIL_LIMIT
    return _DEV_IP_LIMIT, _DEV_EMAIL_LIMIT


async def otp_rate_limit(request: Request) -> None:
    """Sliding-window rate limiter for auth endpoints that send or verify credentials.

    Enforces:
      - production: 5 requests per IP and 3 per email per 10 minutes
      - dev/local: 30 requests per IP and 15 per email per 10 minutes

    IP is read from request.client.host only (no X-Forwarded-For).
    Email is extracted from the JSON request body.
    """
    now = time.monotonic()
    ip = (request.client.host or "") if request.client else ""
    ip_limit, email_limit = _limits()

    _prune(_ip_times[ip], now)
    if len(_ip_times[ip]) >= ip_limit:
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
        if len(_email_times[email]) >= email_limit:
            raise HTTPException(
                status_code=429,
                detail="Too many requests for this email. Try again later.",
            )
        _email_times[email].append(now)
