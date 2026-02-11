from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services.db import (
    get_or_create_user,
    create_session,
    delete_session,
)
from deps import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str


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
        secure=False,
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
