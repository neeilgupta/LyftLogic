from fastapi import HTTPException, Request
from services.db import get_user_by_session


def get_current_user(request: Request):
    token = request.cookies.get("ll_session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = get_user_by_session(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user


def get_optional_current_user(request: Request):
    token = request.cookies.get("ll_session")
    if not token:
        return None

    return get_user_by_session(token)
