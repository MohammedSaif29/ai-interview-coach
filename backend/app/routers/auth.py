"""Accounts: signup, login, logout, 'who am I', and account settings."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import COOKIE_NAME, get_current_user
from app.models import User
from app.rate_limit import (
    client_ip,
    login_attempts_per_ip,
    login_failures,
    sensitive_changes,
    signups_per_ip,
)
from app.schemas import AccountDelete, PasswordChange, UserCreate, UserLogin, UserOut, UserUpdate
from app.security import DUMMY_HASH, create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def set_login_cookie(response: Response, user: User) -> None:
    """Stores the token in a cookie the browser sends back automatically."""
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_access_token(user.id, user.hashed_password),
        httponly=True,                  # JavaScript can't read it, so XSS can't steal it
        secure=settings.cookie_secure,  # HTTPS-only in production
        samesite="lax",                 # not sent on requests from other websites (CSRF protection)
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def clear_login_cookie(response: Response) -> None:
    response.delete_cookie(
        COOKIE_NAME, path="/", httponly=True, secure=settings.cookie_secure, samesite="lax"
    )


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):
    signups_per_ip.hit(client_ip(request))
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

    set_login_cookie(response, user)
    return user


@router.post("/login", response_model=UserOut)
def login(data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    email = data.email.lower()
    ip = client_ip(request)
    failure_key = f"{ip}:{email}"

    login_attempts_per_ip.hit(ip)       # every attempt counts towards the per-IP limit
    login_failures.check(failure_key)  # blocked if this email had too many recent failures

    user = db.scalar(select(User).where(User.email == email))
    # Always check a password, even if the user doesn't exist (see DUMMY_HASH).
    password_ok = verify_password(data.password, user.hashed_password if user else DUMMY_HASH)

    if user is None or not password_ok:
        login_failures.record(failure_key)  # only FAILED attempts count here
        # Same message for both cases, so attackers can't tell which part was wrong.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")

    set_login_cookie(response, user)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    clear_login_cookie(response)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    """Login-only route: returns the logged-in user."""
    return user


@router.patch("/me", response_model=UserOut)
def update_me(data: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """PATCH = change part of something. Here: just the name."""
    user.name = data.name.strip()
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: PasswordChange,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sensitive_changes.hit(f"user:{user.id}")
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Your current password is incorrect.")
    if data.new_password == data.current_password:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Choose a new password that's different from your current one.")

    user.hashed_password = hash_password(data.new_password)
    db.commit()
    # The password fingerprint changed, so every other device is now logged out.
    # Give THIS browser a fresh token so the user stays logged in here.
    set_login_cookie(response, user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    data: AccountDelete,
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sensitive_changes.hit(f"user:{user.id}")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That password is incorrect.")

    db.delete(user)  # cascade: deletes all of the user's sessions too (see models.py)
    db.commit()
    clear_login_cookie(response)
