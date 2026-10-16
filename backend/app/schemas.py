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

from app.question_bank import role_label, target_label


def check_password_length(value: str) -> str:
    # bcrypt (our hashing algorithm) only reads the first 72 bytes.
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password is too long (max 72 bytes)")
    return value


class UserCreate(BaseModel):
    """What the frontend sends to sign up."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return check_password_length(value)


class UserUpdate(BaseModel):
    """Changing your name on the Settings page."""
    name: str = Field(min_length=1, max_length=100)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        return check_password_length(value)


class AccountDelete(BaseModel):
    """Deleting an account needs the password, so a borrowed laptop can't do it."""
    password: str


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


# ---------- AI coach ----------

class CoachMessageIn(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CoachMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime

    @field_serializer("created_at")
    def created_at_utc(self, value: datetime) -> datetime:
        return as_utc(value)


# ---------- Resume review ----------

class ResumeSection(BaseModel):
    name: str
    status: Literal["strong", "needs_work", "missing"]
    feedback: str

    @field_validator("status", mode="before")
    @classmethod
    def normalise_status(cls, value):
        # Accept small variations like "Needs work" from the AI
        cleaned = str(value).strip().lower().replace(" ", "_").replace("-", "_")
        return cleaned if cleaned in ("strong", "needs_work", "missing") else "needs_work"


class ResumeRewrite(BaseModel):
    original: str
    improved: str


class ResumeReview(BaseModel):
    """The AI's review. Also used to validate what the AI sends back."""
    overall_score: int
    summary: str
    sections: list[ResumeSection]
    strengths: list[str]
    improvements: list[str]
    rewrites: list[ResumeRewrite]
    keywords_to_add: list[str]
    interview_questions: list[str]

    @field_validator("overall_score")
    @classmethod
    def score_in_range(cls, value: int) -> int:
        return max(1, min(100, int(value)))

    @field_validator("strengths", "improvements", "keywords_to_add", "interview_questions")
    @classmethod
    def clean_lists(cls, items: list[str], info) -> list[str]:
        limits = {"strengths": 4, "improvements": 5, "keywords_to_add": 8, "interview_questions": 5}
        return [item.strip() for item in items if item.strip()][: limits[info.field_name]]

    @field_validator("sections")
    @classmethod
    def at_most_eight_sections(cls, items):
        return items[:8]

    @field_validator("rewrites")
    @classmethod
    def at_most_three_rewrites(cls, items):
        return items[:3]


class ResumeCheck(BaseModel):
    id: str
    label: str
    passed: bool
    tip: str


class ResumeSummary(BaseModel):
    """One row in the list of past reviews."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    target_role: str
    score: int
    created_at: datetime

    @computed_field
    @property
    def target_label(self) -> str:
        return target_label(self.target_role)

    @field_serializer("created_at")
    def created_at_utc(self, value: datetime) -> datetime:
        return as_utc(value)


class ResumeOut(ResumeSummary):
    page_count: int
    word_count: int
    checks: list[ResumeCheck]
    review: ResumeReview


# ---------- Company mock tests ----------

class TestSubmit(BaseModel):
    """The student's answers: question id -> the option they picked (0-3, as shown), or null if skipped."""
    answers: dict[str, int | None] = Field(default_factory=dict, max_length=100)
    auto_submitted: bool = False  # true when the timer ran out and the page submitted by itself

    @field_validator("answers")
    @classmethod
    def valid_choices(cls, answers: dict[str, int | None]) -> dict[str, int | None]:
        for qid, choice in answers.items():
            if len(qid) > 30:
                raise ValueError("Unknown question")
            if choice is not None and not 0 <= choice <= 3:
                raise ValueError("Each answer must be one of the four options")
        return answers
