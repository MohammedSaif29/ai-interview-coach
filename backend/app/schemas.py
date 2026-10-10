"""Schemas: the shape of data coming IN to the API and going OUT of it.

Pydantic checks every request against these. Bad input is rejected with a
422 error before it ever reaches our code.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """What the frontend sends to sign up."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt (our hashing algorithm) only reads the first 72 bytes.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return value


class UserLogin(BaseModel):
    """What the frontend sends to log in."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """What we send back. Notice: NO password field, so it can never leak."""
    model_config = ConfigDict(from_attributes=True)  # lets us return a User model directly

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class TranscriptWord(BaseModel):
    """One spoken word with when it started and ended (in seconds)."""
    word: str
    start: float
    end: float


class TranscriptOut(BaseModel):
    """What the transcribe endpoint sends back."""
    transcript: str
    duration_seconds: float
    words: list[TranscriptWord]
