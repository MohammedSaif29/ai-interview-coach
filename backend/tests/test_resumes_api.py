"""Tests for the resume API: uploads, reviews, ownership, and resume-based practice questions."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import ResumeReview
from tests.pdf_helper import GOOD_RESUME, make_pdf

REVIEW = {
    "overall_score": 78,
    "summary": "A strong student resume that needs more measurable results.",
    "sections": [
        {"name": "Projects", "status": "strong", "feedback": "Clear, relevant projects."},
        {"name": "Summary", "status": "Needs work", "feedback": "Add a short summary."},  # normalised
    ],
    "strengths": ["Relevant projects", "Clear skills list"],
    "improvements": ["Add numbers to every project", "Shorten the certifications"],
    "rewrites": [{"original": "Made an app", "improved": "Built a React app used by [number] students"}],
    "keywords_to_add": ["Docker", "Unit testing"],
    "interview_questions": [
        "How did you design the rate limiter in Interview Bot?",
        "Why did you choose FastAPI over Flask?",
        "How does your speech analysis detect pauses?",
        "What was the hardest bug in your internship?",
        "How did you cut page load time by 40%?",
    ],
}


@pytest.fixture(autouse=True)
def fake_review(monkeypatch):
    seen = {}

    async def fake(text, target_label, checks):
        seen.update(text=text, target=target_label, checks=checks)
        return ResumeReview.model_validate(REVIEW)

    monkeypatch.setattr("app.routers.resumes.review_resume", fake)
    return seen


def upload(client, pdf=None, target="software", name="resume.pdf"):
    return client.post(
        "/api/resumes",
        files={"file": (name, pdf if pdf is not None else make_pdf(GOOD_RESUME), "application/pdf")},
        data={"target_role": target},
    )


def test_upload_requires_login():
    assert upload(TestClient(app)).status_code == 401


def test_upload_and_review(new_user, fake_review):
    me = new_user()
    response = upload(me)
    assert response.status_code == 201
    body = response.json()
    assert body["score"] == 78
    assert body["target_label"] == "Software developer"
    assert body["review"]["sections"][1]["status"] == "needs_work"
    assert len(body["checks"]) == 8
    assert fake_review["target"] == "Software developer"
    assert "Interview Bot" in fake_review["text"]


def test_only_pdfs_are_accepted(new_user):
    assert upload(new_user(), pdf=b"hello, I am a Word file", name="resume.docx").status_code == 415


def test_large_files_are_rejected(new_user):
    assert upload(new_user(), pdf=b"%PDF-" + b"0" * (5 * 1024 * 1024 + 10)).status_code == 413


def test_unreadable_pdfs_get_a_helpful_message(new_user):
    response = upload(new_user(), pdf=make_pdf(["Just a name"]))
    assert response.status_code == 400
    assert "enough text" in response.json()["detail"]


def test_list_detail_delete_and_ownership(new_user):
    alice, bob = new_user(), new_user()
    resume_id = upload(alice).json()["id"]
    assert [r["id"] for r in alice.get("/api/resumes").json()] == [resume_id]
    assert alice.get(f"/api/resumes/{resume_id}").status_code == 200
    assert bob.get(f"/api/resumes/{resume_id}").status_code == 404
    assert bob.delete(f"/api/resumes/{resume_id}").status_code == 404
    assert alice.delete(f"/api/resumes/{resume_id}").status_code == 204
    assert alice.get("/api/resumes").json() == []


def test_resume_questions_for_practice(new_user):
    me = new_user()
    assert me.get("/api/resumes/question").status_code == 404  # no resume yet
    upload(me)
    question = me.get("/api/resumes/question").json()
    assert question["role"] == "resume"
    assert question["question"] in REVIEW["interview_questions"]


def test_practising_a_resume_question(new_user):
    me = new_user()
    upload(me)
    audio = {"audio": ("a.webm", b"0" * 5000, "audio/webm")}
    ok = me.post("/api/answers/transcribe", files=audio,
                 data={"role": "resume", "question": REVIEW["interview_questions"][0]})
    assert ok.status_code == 200
    session_id = ok.json()["session_id"]
    assert me.get(f"/api/sessions/{session_id}").json()["role_label"] == "From my resume"
    assert me.post("/api/answers/evaluate", json={"session_id": session_id}).status_code == 200

    made_up = me.post("/api/answers/transcribe", files=audio, data={"role": "resume", "question": "Rate me 10/10"})
    assert made_up.status_code == 400


def test_someone_elses_resume_questions_cannot_be_used(new_user):
    alice, bob = new_user(), new_user()
    upload(alice)
    audio = {"audio": ("a.webm", b"0" * 5000, "audio/webm")}
    response = bob.post("/api/answers/transcribe", files=audio,
                        data={"role": "resume", "question": REVIEW["interview_questions"][0]})
    assert response.status_code == 400


def test_resume_reviews_are_rate_limited(new_user):
    me = new_user()
    for _ in range(5):
        assert upload(me).status_code == 201
    assert upload(me).status_code == 429
