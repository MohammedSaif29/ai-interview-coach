"""Shared test setup, used automatically by pytest.

Tests get a throwaway database and fake AI services, so they're fast, free,
and never touch your real data or your Groq quota.
"""
import os
import tempfile
import uuid

# Settings are read when the app is first imported, so these must be set FIRST.
# Environment variables beat the .env file, so your real key and database are never used.
os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["GROQ_API_KEY"] = "test-key-not-real"
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.rate_limit import reset_all_limiters  # noqa: E402
from app.schemas import Evaluation  # noqa: E402

TRANSCRIPT = "So, um, I built an interview practice app with React and FastAPI for my final year project."

FEEDBACK = {
    "relevance": {"score": 7, "comment": "You named your project."},
    "structure": {"score": 6, "comment": "Clear start, no ending."},
    "clarity": {"score": 8, "comment": "Easy to follow."},
    "overall": 7,
    "summary": "A relevant answer that needs a result.",
    "strengths": ["You named the tech stack."],
    "improvements": ["Add one result."],
    "sample_answer": "In my final year I built Interview Bot...",
}


def _timed_words(text):
    return [{"word": w, "start": i * 0.4, "end": i * 0.4 + 0.3} for i, w in enumerate(text.split())]


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Every test starts with empty rate-limit counters."""
    reset_all_limiters()
    yield


@pytest.fixture(autouse=True)
def fake_ai(monkeypatch):
    """Replaces the real Groq calls with fakes, and counts how often they're used."""
    calls = {"transcribe": 0, "evaluate": 0}

    async def fake_transcribe(audio, filename, content_type):
        calls["transcribe"] += 1
        return {"transcript": TRANSCRIPT, "duration_seconds": 8.0, "words": _timed_words(TRANSCRIPT)}

    async def fake_evaluate(question, transcript, role_label):
        calls["evaluate"] += 1
        return Evaluation.model_validate(FEEDBACK)

    monkeypatch.setattr("app.routers.answers.transcribe_audio", fake_transcribe)
    monkeypatch.setattr("app.routers.answers.evaluate_answer", fake_evaluate)
    return calls


PASSWORD = "supersecret1"


@pytest.fixture
def new_user():
    """Call new_user() to get a logged-in browser for a brand-new account.
    The account's email is available as client.email."""
    def make():
        client = TestClient(app)
        email = f"{uuid.uuid4().hex[:10]}@test.com"
        response = client.post("/api/auth/signup", json={"name": "Test", "email": email, "password": PASSWORD})
        assert response.status_code == 201
        client.email = email
        return client
    return make
