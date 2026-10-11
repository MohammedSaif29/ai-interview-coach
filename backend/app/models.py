"""Database tables. Each class = one table, each attribute = one column."""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # We store a HASH of the password, never the password itself.
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # One user has many sessions. Deleting a user deletes their sessions too.
    sessions: Mapped[list["PracticeSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class PracticeSession(Base):
    """One recorded answer: the question, what was said, and both scores."""
    __tablename__ = "practice_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # FOREIGN KEY: links each session to the user who recorded it
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    question: Mapped[str] = mapped_column(String(300))
    transcript: Mapped[str] = mapped_column(Text)
    duration_seconds: Mapped[float] = mapped_column(Float)

    # Speech analysis (our own code). The numbers we chart get their own columns...
    speaking_seconds: Mapped[float] = mapped_column(Float)
    words_per_minute: Mapped[int] = mapped_column(Integer)
    filler_count: Mapped[int] = mapped_column(Integer)
    pause_count: Mapped[int] = mapped_column(Integer)
    delivery_score: Mapped[int] = mapped_column(Integer)
    # ...and the full details (marked-up transcript, tips) are stored as JSON
    analysis: Mapped[dict] = mapped_column(JSON)

    # AI feedback: empty (NULL) until the answer has been scored
    content_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    feedback: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped[User] = relationship(back_populates="sessions")
