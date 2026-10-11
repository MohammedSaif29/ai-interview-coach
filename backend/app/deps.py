"""Dependencies: reusable pieces FastAPI runs before a route.

Add `user: User = Depends(get_current_user)` to any route and it becomes
login-only: FastAPI runs this check first and blocks the request if it fails.
"""
import hmac

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import decode_access_token, password_fingerprint

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

    token = decode_access_token(access_token)
    if token is None:
        raise not_logged_in

    user = db.get(User, token["user_id"])
    if user is None:  # e.g. the account was deleted
        raise not_logged_in

    # Was this token issued before the latest password change? Then it's no longer valid.
    # compare_digest takes the same time whether the codes match or not (no timing hints).
    if not hmac.compare_digest(token["pwd"], password_fingerprint(user.hashed_password)):
        raise not_logged_in
    return user
