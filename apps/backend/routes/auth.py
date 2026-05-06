import os
import secrets
import hashlib
import smtplib
import sqlite3
from email.message import EmailMessage

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, Field

from services.db import (
    get_or_create_user,
    create_user_with_password,
    get_user_by_email,
    get_user_by_id,
    set_email_verified,
    create_session,
    delete_session,
    delete_all_sessions_for_user,
    delete_user,
    create_login_code,
    verify_login_code,
    purge_expired_login_codes,
    create_email_verification_token,
    consume_email_verification_token,
    purge_expired_verification_tokens,
    create_password_reset_token,
    consume_password_reset_token,
    update_password_hash,
    purge_expired_reset_tokens,
)
from deps import get_current_user
from routes.dependencies import otp_rate_limit


router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_SECURE = os.getenv("ENV") == "production"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")


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


class ResendVerificationRequest(BaseModel):
    email: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password: str


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


def _send_verification_email(email: str, verification_url: str) -> None:
    if os.getenv("PRINT_OTP_TO_CONSOLE", "0") == "1":
        print(f"[DEV VERIFY] {email}: {verification_url}", flush=True)
        return

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_addr = os.getenv("SMTP_FROM", smtp_user)

    msg = EmailMessage()
    msg["Subject"] = "Verify your LyftLogic email"
    msg["From"] = from_addr
    msg["To"] = email
    msg.set_content(
        f"Click the link below to verify your email address:\n\n{verification_url}\n\n"
        "This link expires in 24 hours. If you did not create a LyftLogic account, you can ignore this email."
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_user:
            server.starttls()
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


def _send_reset_email(email: str, reset_url: str) -> None:
    if os.getenv("PRINT_OTP_TO_CONSOLE", "0") == "1":
        print(f"[DEV RESET] {email}: {reset_url}", flush=True)
        return

    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    from_addr = os.getenv("SMTP_FROM", smtp_user)

    msg = EmailMessage()
    msg["Subject"] = "Reset your LyftLogic password"
    msg["From"] = from_addr
    msg["To"] = email
    msg.set_content(
        f"Click the link below to reset your password:\n\n{reset_url}\n\n"
        "This link expires in 1 hour. If you did not request a password reset, you can ignore this email."
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
def verify_code(req: VerifyCodeRequest, _=Depends(otp_rate_limit)):
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
    full = get_user_by_id(user["id"])
    if not full:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": full["id"],
        "email": full["email"],
        "has_password": full["password_hash"] is not None,
        "created_at": full["created_at"],
        "email_verified": bool(full["email_verified"]),
    }


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


@router.post("/change-password")
def change_password(req: ChangePasswordRequest, user=Depends(get_current_user)):
    full = get_user_by_email(user["email"])
    if not full or not full.get("password_hash"):
        raise HTTPException(status_code=400, detail="Account uses magic link only — no password to change")
    if not bcrypt.checkpw(req.current_password.encode(), full["password_hash"].encode()):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    new_hash = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    update_password_hash(user["id"], new_hash)
    delete_all_sessions_for_user(user["id"])
    resp = JSONResponse({"ok": True, "detail": "Password updated. Please sign in again."})
    resp.delete_cookie("ll_session", path="/")
    return resp


class DeleteAccountRequest(BaseModel):
    password: Optional[str] = None


@router.delete("/account")
def delete_account(req: DeleteAccountRequest, user=Depends(get_current_user)):
    full = get_user_by_email(user["email"])
    if not full:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if full["password_hash"]:
        if not req.password:
            raise HTTPException(status_code=400, detail="Password required to delete account")
        if not bcrypt.checkpw(req.password.encode(), full["password_hash"].encode()):
            raise HTTPException(status_code=400, detail="Incorrect password")
    delete_user(user["id"])
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("ll_session", path="/")
    return resp


@router.post("/register", status_code=202)
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

    token = create_email_verification_token(user["id"])
    verification_url = f"{FRONTEND_URL}/verify-email?token={token}"

    try:
        _send_verification_email(email, verification_url)
    except Exception:
        raise HTTPException(status_code=503, detail="Failed to send verification email. Try again.")

    return {"detail": "Check your email to verify your account before signing in."}


@router.post("/password-login")
def password_login(req: PasswordLoginRequest, _=Depends(otp_rate_limit)):
    email = req.email.strip().lower()
    password = req.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = get_user_by_email(email)

    # Constant-time guard: run checkpw even on miss to prevent timing attacks.
    # Dummy hash is a valid 60-char bcrypt hash so checkpw never raises ValueError.
    _DUMMY_HASH = b"$2b$12$vJa6dzmDB5EA0NqSA9ltJeBNo0idlFKEuxf3zIC8b3RTur0KJgY2C"
    stored = user["password_hash"].encode() if (user and user.get("password_hash")) else _DUMMY_HASH
    try:
        match = bcrypt.checkpw(password.encode(), stored)
    except ValueError:
        match = False

    if not user or not user.get("password_hash") or not match:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.get("email_verified"):
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before signing in. Check your inbox or request a new verification link.",
        )

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


@router.get("/verify-email")
def verify_email(token: str):
    try:
        purge_expired_verification_tokens()
    except Exception:
        pass

    user_id = consume_email_verification_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Verification link is invalid or has expired.")

    set_email_verified(user_id)

    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=500, detail="User not found")

    session_token = create_session(user_id)
    resp = JSONResponse({"id": user["id"], "email": user["email"]})
    resp.set_cookie(
        "ll_session",
        session_token,
        httponly=True,
        samesite="lax",
        secure=COOKIE_SECURE,
        path="/",
    )
    return resp


@router.post("/resend-verification", status_code=202)
def resend_verification(req: ResendVerificationRequest, _=Depends(otp_rate_limit)):
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = get_user_by_email(email)
    # Non-committal: don't reveal if email exists or is already verified
    if user and not user.get("email_verified") and user.get("password_hash"):
        token = create_email_verification_token(user["id"])
        verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
        try:
            _send_verification_email(email, verification_url)
        except Exception:
            raise HTTPException(status_code=503, detail="Failed to send verification email. Try again.")

    return {"detail": "If that address is registered and unverified, a new link has been sent."}


@router.post("/forgot-password", status_code=202)
def forgot_password(req: ForgotPasswordRequest, _=Depends(otp_rate_limit)):
    email = req.email.strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = get_user_by_email(email)
    # Only send reset email for password-based accounts that exist
    if user and user.get("password_hash"):
        token = create_password_reset_token(user["id"])
        reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
        try:
            _send_reset_email(email, reset_url)
        except Exception:
            raise HTTPException(status_code=503, detail="Failed to send reset email. Try again.")

    return {"detail": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    if len(req.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    try:
        purge_expired_reset_tokens()
    except Exception:
        pass

    user_id = consume_password_reset_token(req.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Reset link is invalid or has expired.")

    new_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    update_password_hash(user_id, new_hash)
    delete_all_sessions_for_user(user_id)

    return {"detail": "Password has been reset. You can now sign in."}


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
