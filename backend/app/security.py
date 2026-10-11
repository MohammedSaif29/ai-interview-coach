"""Password hashing and login tokens (JWT)."""
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

ALGORITHM = "HS256"


# ---------- Passwords ----------

def hash_password(password: str) -> str:
    """Turns 'mypassword' into a one-way scrambled string. It can't be reversed."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Hashes the typed password the same way and compares the results."""
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        return False
    return bcrypt.checkpw(password_bytes, hashed.encode("utf-8"))


# Used when someone logs in with an email that doesn't exist. We still run a
# password check so the response takes the same time either way. Otherwise an
# attacker could time responses to discover which emails are registered.
DUMMY_HASH = hash_password("dummy-password-for-timing")


# ---------- Tokens (JWT) ----------

def password_fingerprint(hashed_password: str) -> str:
    """A short code derived from the user's current password hash (and our secret key).
    It goes inside every login token. When the password changes, the fingerprint changes,
    so every older token stops working: "log out everywhere" without a database table."""
    digest = hmac.new(settings.secret_key.encode(), hashed_password.encode(), hashlib.sha256)
    return digest.hexdigest()[:16]


def create_access_token(user_id: int, hashed_password: str) -> str:
    """Creates a signed token that says 'this is user X', valid for a limited time."""
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": str(user_id), "pwd": password_fingerprint(hashed_password), "exp": expires}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Returns {"user_id", "pwd"} if the token is genuine and not expired, otherwise None."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return {"user_id": int(payload["sub"]), "pwd": payload["pwd"]}
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        return None
