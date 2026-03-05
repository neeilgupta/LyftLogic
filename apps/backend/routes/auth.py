import os
import secrets
import hashlib
import smtplib
import sqlite3
from email.message import EmailMessage

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.db import (
    get_or_create_user,
    create_user_with_password,
    get_user_by_email,
    set_email_verified,
    create_session,
    delete_session,
    create_login_code,
    verify_login_code,
    purge_expired_login_codes,
)
from deps import get_current_user
from routes.dependencies import otp_rate_limit


router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_SECURE = os.getenv("ENV") == "production"


class LoginRequest(BaseModel):
    email: str


class RegisterRequest(BaseModel):
    email: str
    password: str


class PasswordLoginRequest(BaseModel):
    email: str
    password: str


class RequestCodeRequest(BaseModel):
    email: str


class VerifyCodeRequest(BaseModel):
    email: str
    code: str


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _send_otp(email: str, code: str) -> None:
    if os.getenv("PRINT_OTP_TO_CONSOLE", "0") == "1":
        print(f"[DEV OTP] {email}: {code}", flush=True)
        return

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_addr = os.getenv("SMTP_FROM", smtp_user)

    msg = EmailMessage()
    msg["Subject"] = "Your LyftLogic login code"
    msg["From"] = from_addr
    msg["To"] = email
    msg.set_content(
        f"Your one-time login code is: {code}\n\nExpires in 15 minutes. Do not share this code."
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_user:
            server.starttls()
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


@router.post("/request-code", status_code=202)
async def request_code(req: RequestCodeRequest, _=Depends(otp_rate_limit)):
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    code = str(secrets.randbelow(1_000_000)).zfill(6)
    code_hash = _hash_code(code)

    try:
        purge_expired_login_codes()
    except Exception:
        pass

    create_login_code(email, code_hash)

    try:
        _send_otp(email, code)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to send code. Try again.")

    return {"detail": "If that address is valid, a code has been sent."}


@router.post("/verify-code")
def verify_code(req: VerifyCodeRequest):
    email = req.email.strip().lower()
    code = (req.code or "").strip()

    if not email or not code:
        raise HTTPException(status_code=400, detail="Email and code are required")

    ok = verify_login_code(email, _hash_code(code))
    if not ok:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user = get_or_create_user(email)
    set_email_verified(user["id"])
    token = create_session(user["id"])

    resp = JSONResponse({"id": user["id"], "email": user["email"]})
    resp.set_cookie(
        "ll_session",
        token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )
    return resp


@router.post("/logout")
def logout(request: Request):
    token = request.cookies.get("ll_session")
    if token:
        delete_session(token)

    resp = JSONResponse({"ok": True})
    resp.delete_cookie("ll_session", path="/")
    return resp


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user["id"], "email": user["email"]}


@router.post("/register", status_code=201)
def register(req: RegisterRequest):
    email = req.email.strip().lower()
    password = req.password

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    try:
        user = create_user_with_password(email, password_hash)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists")

    token = create_session(user["id"])

    resp = JSONResponse({"id": user["id"], "email": user["email"]}, status_code=201)
    resp.set_cookie(
        "ll_session",
        token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )
    return resp


@router.post("/password-login")
def password_login(req: PasswordLoginRequest):
    email = req.email.strip().lower()
    password = req.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = get_user_by_email(email)

    # Constant-time guard: run checkpw even on miss to prevent timing attacks
    dummy_hash = b"$2b$12$invalidhashpadding000000000000000000000000000000000000u"
    stored = user["password_hash"].encode() if (user and user.get("password_hash")) else dummy_hash
    match = bcrypt.checkpw(password.encode(), stored)

    if not user or not user.get("password_hash") or not match:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_session(user["id"])

    resp = JSONResponse({"id": user["id"], "email": user["email"]})
    resp.set_cookie(
        "ll_session",
        token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )
    return resp


# Dev/CI bypass — allows instant login without OTP. NEVER enable in production.
if os.getenv("ALLOW_INSECURE_LOGIN", "0") == "1":
    @router.post("/login")
    def login(req: LoginRequest):
        email = req.email.strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        user = get_or_create_user(email)
        token = create_session(user["id"])

        resp = JSONResponse({"id": user["id"], "email": user["email"]})
        resp.set_cookie(
            "ll_session",
            token,
            httponly=True,
            samesite="lax",
            secure=COOKIE_SECURE,
            path="/",
        )
        return resp
