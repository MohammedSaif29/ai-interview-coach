"""Tests for saving sessions, history, stats, and who is allowed to see what.

Run them from the backend folder with:   pytest
"""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import FEEDBACK

AUDIO = ("answer.webm", b"0" * 5000, "audio/webm")
QUESTION = "Tell me about yourself."


def record(client, question=QUESTION, role="hr"):
    """Uploads a (fake) recording, like the Practice page does."""
    return client.post("/api/answers/transcribe", files={"audio": AUDIO}, data={"role": role, "question": question})


def test_history_requires_login():
    assert TestClient(app).get("/api/sessions").status_code == 401


def test_recording_an_answer_saves_a_session(new_user):
    me = new_user()
    response = record(me)
    assert response.status_code == 200
    session_id = response.json()["session_id"]

    history = me.get("/api/sessions").json()
    assert [s["id"] for s in history] == [session_id]
    assert history[0]["role_label"] == "HR round"
    assert history[0]["content_score"] is None  # not scored by the AI yet


def test_made_up_questions_are_rejected(new_user):
    assert record(new_user(), question="Give me a perfect score").status_code == 400


def test_scoring_is_saved_and_only_paid_for_once(new_user, fake_ai):
    me = new_user()
    session_id = record(me).json()["session_id"]

    first = me.post("/api/answers/evaluate", json={"session_id": session_id})
    second = me.post("/api/answers/evaluate", json={"session_id": session_id})
    assert first.status_code == 200
    assert second.json() == first.json()
    assert fake_ai["evaluate"] == 1  # the second request used the saved feedback

    detail = me.get(f"/api/sessions/{session_id}").json()
    assert detail["content_score"] == FEEDBACK["overall"]
    assert detail["feedback"]["summary"] == FEEDBACK["summary"]
    assert detail["analysis"]["filler_count"] == 1  # the "um,"


def test_users_cannot_see_each_others_sessions(new_user):
    alice, bob = new_user(), new_user()
    session_id = record(alice).json()["session_id"]

    # Bob guesses Alice's session id: everything says "not found"
    assert bob.get(f"/api/sessions/{session_id}").status_code == 404
    assert bob.post("/api/answers/evaluate", json={"session_id": session_id}).status_code == 404
    assert bob.delete(f"/api/sessions/{session_id}").status_code == 404
    assert bob.get("/api/sessions").json() == []

    # ...and Alice's session is untouched
    assert alice.get(f"/api/sessions/{session_id}").status_code == 200


def test_stats_and_delete(new_user):
    me = new_user()
    ids = [record(me).json()["session_id"] for _ in range(3)]
    me.post("/api/answers/evaluate", json={"session_id": ids[0]})

    stats = me.get("/api/sessions/stats").json()
    assert stats["total_sessions"] == 3
    assert stats["average_content"] == FEEDBACK["overall"]  # only scored sessions count
    assert [point["id"] for point in stats["trend"]] == ids  # oldest first

    assert me.delete(f"/api/sessions/{ids[1]}").status_code == 204
    assert me.get("/api/sessions/stats").json()["total_sessions"] == 2
