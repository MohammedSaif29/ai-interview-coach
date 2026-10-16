"""Tests for the AI coach chat. The real AI is replaced with a fake that records
what it was sent, so we can check the coach gets the right information."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.groq_client import GroqError
from tests.conftest import PASSWORD

AUDIO = {"audio": ("a.webm", b"0" * 5000, "audio/webm")}
FORM = {"role": "software", "question": "Explain a project you worked on and your role in it."}


@pytest.fixture
def fake_coach(monkeypatch):
    """Replaces the AI with a fake that replies in three pieces and remembers what it saw."""
    seen = {"calls": []}

    async def fake_stream(messages):
        seen["calls"].append(messages)
        for piece in ["Great ", "question! ", "Practise daily."]:
            yield piece

    monkeypatch.setattr("app.services.coach.stream_chat", fake_stream)
    return seen


def ask(client, text):
    return client.post("/api/coach/messages", json={"content": text})


def test_coach_requires_login():
    assert TestClient(app).get("/api/coach/messages").status_code == 401


def test_reply_is_streamed_and_both_messages_are_saved(new_user, fake_coach):
    me = new_user()
    response = ask(me, "How do I prepare for HR rounds?")
    assert response.status_code == 200
    assert response.text == "Great question! Practise daily."

    history = me.get("/api/coach/messages").json()
    assert [(m["role"], m["content"]) for m in history] == [
        ("user", "How do I prepare for HR rounds?"),
        ("assistant", "Great question! Practise daily."),
    ]


def test_coach_sees_the_students_real_practice_data(new_user, fake_coach):
    me = new_user()
    session_id = me.post("/api/answers/transcribe", files=AUDIO, data=FORM).json()["session_id"]
    me.post("/api/answers/evaluate", json={"session_id": session_id})

    ask(me, "What should I work on?")
    context = fake_coach["calls"][0][1]["content"]
    assert "Explain a project you worked on" in context
    assert "content 7/10" in context            # the score from the (fake) AI feedback
    assert "Add one result." in context         # the AI's improvement note


def test_coach_knows_when_there_is_no_practice_yet(new_user, fake_coach):
    me = new_user()
    ask(me, "Hi")
    assert "haven't recorded any practice" in fake_coach["calls"][0][1]["content"]


def test_coach_remembers_the_conversation(new_user, fake_coach):
    me = new_user()
    ask(me, "First question")
    ask(me, "Second question")
    second_call = fake_coach["calls"][1]
    assert [m["content"] for m in second_call[2:]] == [
        "First question", "Great question! Practise daily.", "Second question",
    ]


def test_clear_chat(new_user, fake_coach):
    me = new_user()
    ask(me, "Hello")
    assert me.delete("/api/coach/messages").status_code == 204
    assert me.get("/api/coach/messages").json() == []


def test_very_long_messages_are_rejected(new_user, fake_coach):
    assert ask(new_user(), "x" * 2001).status_code == 422


def test_coach_messages_are_rate_limited(new_user, fake_coach):
    me = new_user()
    for i in range(20):
        assert ask(me, f"Question {i}").status_code == 200
    assert ask(me, "One too many").status_code == 429


def test_failed_reply_is_an_error_and_the_question_is_not_saved(new_user, monkeypatch):
    async def broken_stream(messages):
        raise GroqError("Too many requests to the AI service right now. Wait a minute and try again.", 429)
        yield  # makes this an async generator

    monkeypatch.setattr("app.services.coach.stream_chat", broken_stream)
    me = new_user()
    response = ask(me, "Hello?")
    assert response.status_code == 502
    assert "Too many requests" in response.json()["detail"]
    assert me.get("/api/coach/messages").json() == []


def test_deleting_the_account_deletes_the_chat(new_user, fake_coach):
    from app.database import SessionLocal
    from app.models import CoachMessage

    me = new_user()
    my_id = me.get("/api/auth/me").json()["id"]
    ask(me, "Hello")
    assert me.request("DELETE", "/api/auth/me", json={"password": PASSWORD}).status_code == 204
    with SessionLocal() as db:
        # Only count THIS user's messages: other tests share the same test database
        assert db.query(CoachMessage).filter(CoachMessage.user_id == my_id).count() == 0
