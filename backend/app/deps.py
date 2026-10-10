"""Dependencies: reusable pieces FastAPI runs before a route.

Add `user: User = Depends(get_current_user)` to any route and it becomes
login-only: FastAPI runs this check first and blocks the request if it fails.
"""
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token

COOKIE_NAME = "access_token"


def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> User:
    not_logged_in = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )
    if not access_token:
        raise not_logged_in

    user_id = decode_access_token(access_token)
    if user_id is None:
        raise not_logged_in

    user = db.get(User, user_id)
    if user is None:
        raise not_logged_in
    return user
