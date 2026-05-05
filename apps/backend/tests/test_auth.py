from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
from fastapi.testclient import TestClient

import routes.auth as auth_routes
import routes.dependencies as rate_limits
from main import app
from services import db


def _client_without_overrides() -> TestClient:
    app.dependency_overrides.clear()
    db.init_db()
    return TestClient(app)


def _make_user(email: str, password: str = "oldpassword123") -> tuple[int, str]:
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    with db._conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO users(email, password_hash, email_verified)
            VALUES (?, ?, 1)
            """,
            (email, password_hash),
        )
        return cur.lastrowid, password_hash


def test_unknown_email_password_login_runs_dummy_bcrypt(monkeypatch):
    client = _client_without_overrides()
    calls: list[bytes] = []

    def fake_checkpw(password: bytes, stored: bytes) -> bool:
        calls.append(stored)
        return False

    monkeypatch.setattr(auth_routes.bcrypt, "checkpw", fake_checkpw)

    response = client.post(
        "/auth/password-login",
        json={"email": "missing-phase1@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert len(calls) == 1
    assert calls[0].startswith(b"$2b$")


def test_sessions_invalidated_on_password_change():
    client = _client_without_overrides()
    email = f"phase1-change-password-{uuid4().hex}@example.com"
    _make_user(email)

    login = client.post("/auth/password-login", json={"email": email, "password": "oldpassword123"})
    assert login.status_code == 200, login.text
    token = login.cookies.get("ll_session")
    assert token

    change = client.post(
        "/auth/change-password",
        json={"current_password": "oldpassword123", "new_password": "newpassword123"},
        cookies={"ll_session": token},
    )
    assert change.status_code == 200, change.text

    me = client.get("/auth/me", cookies={"ll_session": token})
    assert me.status_code == 401


def test_otp_rate_limiting_rejects_after_threshold(monkeypatch):
    client = _client_without_overrides()
    rate_limits._ip_times.clear()
    rate_limits._email_times.clear()
    monkeypatch.setattr(auth_routes, "_send_otp", lambda email, code: None)

    payload = {"email": "phase1-rate-limit@example.com"}
    statuses = [client.post("/auth/request-code", json=payload).status_code for _ in range(4)]

    assert statuses[:3] == [202, 202, 202]
    assert statuses[3] == 429


def test_expired_session_rejected():
    client = _client_without_overrides()
    user_id, _ = _make_user(f"phase1-expired-session-{uuid4().hex}@example.com")
    expired = (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    token = f"phase1-expired-token-{uuid4().hex}"

    with db._conn() as conn:
        conn.execute(
            "INSERT INTO sessions(token, user_id, expires_at) VALUES (?, ?, ?)",
            (token, user_id, expired),
        )

    response = client.get("/auth/me", cookies={"ll_session": token})

    assert response.status_code == 401
