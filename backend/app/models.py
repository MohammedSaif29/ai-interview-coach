"""Database tables. Each class = one table, each attribute = one column."""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
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
    coach_messages: Mapped[list["CoachMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    resumes: Mapped[list["Resume"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    test_attempts: Mapped[list["TestAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")


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


class CoachMessage(Base):
    """One message in a user's conversation with the AI coach."""
    __tablename__ = "coach_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(10))  # "user" or "assistant"
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped[User] = relationship(back_populates="coach_messages")


class Resume(Base):
    """One uploaded resume and its review. We keep the extracted text, never the PDF file."""
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(150))
    target_role: Mapped[str] = mapped_column(String(20))
    page_count: Mapped[int] = mapped_column(Integer)
    word_count: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    checks: Mapped[list] = mapped_column(JSON)   # the automatic ATS checks
    review: Mapped[dict] = mapped_column(JSON)   # the AI review
    score: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    user: Mapped[User] = relationship(back_populates="resumes")


class TestAttempt(Base):
    """One company mock test: which questions were asked, and (after submitting) the result."""
    __tablename__ = "test_attempts"
    __test__ = False  # its name starts with "Test", so tell pytest it isn't a test class

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[str] = mapped_column(String(30), index=True)
    # Each item: {"id": question id, "section": section name, "order": how the 4 options were shuffled}
    questions: Mapped[list] = mapped_column(JSON)
    time_limit_seconds: Mapped[int] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

    # Filled in when the test is submitted
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    answers: Mapped[dict | None] = mapped_column(JSON, nullable=True)   # question id -> option shown (0-3) or null
    correct_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)  # percentage
    section_scores: Mapped[list | None] = mapped_column(JSON, nullable=True)
    auto_submitted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="test_attempts")
