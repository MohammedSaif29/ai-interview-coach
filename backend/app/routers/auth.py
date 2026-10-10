"""Signup, login, logout, and 'who am I'."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import COOKIE_NAME, get_current_user
from app.models import User
from app.schemas import UserCreate, UserLogin, UserOut
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def set_login_cookie(response: Response, user_id: int) -> None:
    """Stores the token in a cookie the browser sends back automatically."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user_id),
        httponly=True,                  # JavaScript can't read it, so XSS can't steal it
        secure=settings.cookie_secure,  # HTTPS-only in production
        samesite="lax",                 # not sent on requests from other websites (CSRF protection)
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, response: Response, db: Session = Depends(get_db)):
    email = data.email.lower()

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(name=data.name.strip(), email=email, hashed_password=hash_password(data.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # two signups with the same email at the exact same moment
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")
    db.refresh(user)

    set_login_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))

    # Always check a password, even if the user doesn't exist (see DUMMY_HASH).
    password_ok = verify_password(data.password, user.hashed_password if user else DUMMY_HASH)

    if user is None or not password_ok:
        # Same message for both cases, so attackers can't tell which part was wrong.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    set_login_cookie(response, user.id)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie(
        COOKIE_NAME, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax"
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Login-only route: returns the logged-in user."""
    return user
