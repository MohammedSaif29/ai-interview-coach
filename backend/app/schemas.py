"""Schemas: the shape of data coming IN to the API and going OUT of it.

Pydantic checks every request against these. Bad input is rejected with a
422 error before it ever reaches our code.
"""
from datetime import datetime, timezone
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from app.question_bank import role_label


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


def as_utc(value: datetime) -> datetime:
    """SQLite forgets time zones, so a saved UTC time comes back "naive".
    Mark it as UTC again, so browsers convert it to the user's local time correctly."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class UserOut(BaseModel):
    """What we send back. Notice: NO password field, so it can never leak."""
    model_config = ConfigDict(from_attributes=True)  # lets us return a User model directly

    id: int
    name: str
    email: EmailStr
    created_at: datetime

    @field_serializer("created_at")
    def created_at_utc(self, value: datetime) -> datetime:
        return as_utc(value)


class TranscriptWord(BaseModel):
    """One spoken word with when it started and ended (in seconds)."""
    word: str
    start: float
    end: float


class SpeechToken(BaseModel):
    """One word of the transcript, marked up for display."""
    text: str
    filler: bool
    pause_seconds: float | None  # silence AFTER this word, if it was notable
    pause_kind: Literal["hesitation", "long"] | None


class FillerCount(BaseModel):
    text: str
    count: int


class SpeechAnalysis(BaseModel):
    """How the answer was spoken (calculated by our own code, see speech_analysis.py)."""
    word_count: int
    speaking_seconds: float
    words_per_minute: int
    pace: str
    filler_count: int
    filler_words: list[FillerCount]
    hesitation_count: int
    long_pause_count: int
    delivery_score: int
    tips: list[str]
    tokens: list[SpeechToken]


class TranscriptOut(BaseModel):
    """What the transcribe endpoint sends back."""
    session_id: int | None  # the saved session (None if no speech was detected)
    transcript: str
    duration_seconds: float
    words: list[TranscriptWord]
    analysis: SpeechAnalysis


# ---------- AI evaluation ----------

class EvaluateRequest(BaseModel):
    """What the frontend sends to get feedback: just WHICH saved session to score.
    The question and transcript are read from the database, so they can't be faked."""
    session_id: int


def _clamp_score(value: int) -> int:
    return max(1, min(10, int(value)))


class Criterion(BaseModel):
    score: int
    comment: str

    @field_validator("score")
    @classmethod
    def score_in_range(cls, value: int) -> int:
        return _clamp_score(value)  # never trust the AI to stay within 1-10


class Evaluation(BaseModel):
    """The AI's feedback. Also used to validate what the AI sends back."""
    overall: int
    summary: str
    relevance: Criterion
    structure: Criterion
    clarity: Criterion
    strengths: list[str]
    improvements: list[str]
    sample_answer: str

    @model_validator(mode="before")
    @classmethod
    def fill_missing_overall(cls, data):
        # If the AI forgot the overall score, use the average of the three criteria
        if isinstance(data, dict) and data.get("overall") is None:
            try:
                scores = [_clamp_score(data[name]["score"]) for name in ("relevance", "structure", "clarity")]
                data = {**data, "overall": round(sum(scores) / 3)}
            except (KeyError, TypeError, ValueError):
                pass  # can't calculate it; normal validation will report the problem
        return data

    @field_validator("overall")
    @classmethod
    def overall_in_range(cls, value: int) -> int:
        return _clamp_score(value)

    @field_validator("strengths", "improvements")
    @classmethod
    def at_most_three(cls, items: list[str]) -> list[str]:
        return [item.strip() for item in items if item.strip()][:3]


# ---------- Saved sessions ----------

class SessionSummary(BaseModel):
    """One row in the history list."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    question: str
    content_score: int | None
    delivery_score: int
    words_per_minute: int
    filler_count: int
    created_at: datetime

    @computed_field
    @property
    def role_label(self) -> str:
        return role_label(self.role)

    @field_serializer("created_at")
    def created_at_utc(self, value: datetime) -> datetime:
        return as_utc(value)


class SessionDetail(SessionSummary):
    """Everything about one session, for its own page."""
    transcript: str
    duration_seconds: float
    analysis: SpeechAnalysis
    feedback: Evaluation | None


class TrendPoint(BaseModel):
    """One session's numbers, for the progress charts."""
    id: int
    created_at: datetime
    content_score: int | None
    delivery_score: int
    fillers_per_minute: float
    words_per_minute: int

    @field_serializer("created_at")
    def created_at_utc(self, value: datetime) -> datetime:
        return as_utc(value)


class StatsOut(BaseModel):
    total_sessions: int
    average_content: float | None
    average_delivery: float | None
    trend: list[TrendPoint]  # oldest first, last 20 sessions
