"""Schemas: the shape of data coming IN to the API and going OUT of it.

Pydantic checks every request against these. Bad input is rejected with a
422 error before it ever reaches our code.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


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
    transcript: str
    duration_seconds: float
    words: list[TranscriptWord]
    analysis: SpeechAnalysis


# ---------- AI evaluation ----------

class EvaluateRequest(BaseModel):
    """What the frontend sends to get feedback on an answer."""
    question: str = Field(min_length=1, max_length=300)
    role: str = Field(default="hr", max_length=20)
    transcript: str = Field(min_length=1, max_length=8000)


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
