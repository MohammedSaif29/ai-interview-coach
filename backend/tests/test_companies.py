"""Tests for company prep: the data itself, the mock tests, marking, and security."""
from datetime import timedelta

from fastapi.testclient import TestClient

from app.aptitude_bank import CATEGORIES, QUESTIONS, QUESTIONS_BY_ID, questions_in
from app.companies import COMPANIES, level_for, question_count
from app.database import SessionLocal
from app.main import app
from app.models import TestAttempt
from tests.conftest import PASSWORD


# ---------- The data ----------

def test_every_question_has_four_different_options():
    assert len({q["id"] for q in QUESTIONS}) == len(QUESTIONS)
    for q in QUESTIONS:
        options = [q["correct"], *q["wrong"]]
        assert len(options) == 4 and len(set(options)) == 4, q["id"]
        assert q["category"] in CATEGORIES and q["explain"]


def test_every_company_mock_can_be_built_from_the_bank():
    for company in COMPANIES:
        needed: dict[str, int] = {}
        for section in company["mock"]["sections"]:
            for category, count in section["pick"].items():
                needed[category] = needed.get(category, 0) + count
        for category, count in needed.items():
            assert count <= len(questions_in(category)), (company["id"], category)
        # levels go from highest to lowest and always end with a catch-all
        minimums = [level["min"] for level in company["levels"]]
        assert minimums == sorted(minimums, reverse=True) and minimums[-1] == 0
        assert company["sources"], company["id"]


def test_level_for_picks_the_highest_level_reached():
    tcs = next(c for c in COMPANIES if c["id"] == "tcs")
    assert level_for(tcs, 90)["label"] == "Prime-level"
    assert level_for(tcs, 65)["label"] == "Digital-level"
    assert level_for(tcs, 10)["label"].startswith("Below")


# ---------- Browsing companies ----------

def test_companies_need_login():
    assert TestClient(app).get("/api/companies").status_code == 401


def test_list_and_detail(new_user):
    client = new_user()
    companies = client.get("/api/companies").json()
    assert {"tcs", "infosys", "amazon", "zoho"} <= {c["id"] for c in companies}
    assert {c["kind"] for c in companies} == {"service", "product"}

    detail = client.get("/api/companies/tcs").json()
    assert [r["name"] for r in detail["roles"]] == ["Ninja", "Digital", "Prime"]
    assert detail["mock"]["question_count"] == question_count(next(c for c in COMPANIES if c["id"] == "tcs"))
    assert detail["attempts"] == []
    assert client.get("/api/companies/nope").status_code == 404


# ---------- Taking a test ----------

def correct_answers(paper):
    """Work out the right option for each question, the way only the server can."""
    answers = {}
    for section in paper["sections"]:
        for question in section["questions"]:
            answers[question["id"]] = question["options"].index(QUESTIONS_BY_ID[question["id"]]["correct"])
    return answers


def test_the_paper_never_contains_answers(new_user):
    client = new_user()
    paper = client.post("/api/companies/tcs/tests").json()
    questions = [q for s in paper["sections"] for q in s["questions"]]
    assert all(set(q) == {"id", "text", "code", "options"} for q in questions)  # no answer, no explanation
    assert len(questions) == paper_size("tcs")
    assert len({q["id"] for q in questions}) == len(questions)  # no repeats
    assert [s["name"] for s in paper["sections"]] == [s["name"] for s in company("tcs")["mock"]["sections"]]
    assert paper["time_limit_seconds"] == 40 * 60


def test_full_marks_and_review(new_user):
    client = new_user()
    paper = client.post("/api/companies/amazon/tests").json()
    result = client.post(f"/api/tests/{paper['id']}/submit", json={"answers": correct_answers(paper)}).json()
    assert result["score"] == 100 and result["correct"] == result["total"] == paper_size("amazon")
    assert result["level"]["label"] == "Strong fundamentals"
    assert all(item["chosen"] == item["correct"] for item in result["review"])
    assert sum(s["total"] for s in result["sections"]) == result["total"]

    # It now shows in history and as the best score
    assert client.get("/api/companies/amazon").json()["attempts"][0]["score"] == 100
    assert next(c for c in client.get("/api/companies").json() if c["id"] == "amazon")["best_score"] == 100
    assert client.get(f"/api/tests/{paper['id']}").json()["status"] == "submitted"


def test_skipped_and_wrong_answers_score_zero(new_user):
    client = new_user()
    paper = client.post("/api/companies/zoho/tests").json()
    right = correct_answers(paper)
    wrong = {qid: (choice + 1) % 4 for qid, choice in right.items()}
    first = next(iter(wrong))
    wrong[first] = None  # skipped
    result = client.post(f"/api/tests/{paper['id']}/submit", json={"answers": wrong}).json()
    assert result["score"] == 0
    assert next(item for item in result["review"] if item["id"] == first)["chosen"] is None


def test_answers_for_other_questions_are_ignored(new_user):
    client = new_user()
    paper = client.post("/api/companies/wipro/tests").json()
    asked = {q["id"] for s in paper["sections"] for q in s["questions"]}
    outsider = next(q["id"] for q in QUESTIONS if q["id"] not in asked)
    result = client.post(f"/api/tests/{paper['id']}/submit", json={"answers": {outsider: 0}}).json()
    assert result["score"] == 0 and outsider not in {item["id"] for item in result["review"]}


def test_invalid_choice_is_rejected(new_user):
    client = new_user()
    paper = client.post("/api/companies/tcs/tests").json()
    qid = paper["sections"][0]["questions"][0]["id"]
    assert client.post(f"/api/tests/{paper['id']}/submit", json={"answers": {qid: 7}}).status_code == 422


def test_a_test_can_only_be_submitted_once(new_user):
    client = new_user()
    paper = client.post("/api/companies/tcs/tests").json()
    assert client.post(f"/api/tests/{paper['id']}/submit", json={"answers": {}}).status_code == 200
    assert client.post(f"/api/tests/{paper['id']}/submit", json={"answers": correct_answers(paper)}).status_code == 409


def test_refreshing_mid_test_returns_the_same_paper(new_user):
    client = new_user()
    paper = client.post("/api/companies/infosys/tests").json()
    again = client.get(f"/api/tests/{paper['id']}").json()
    assert again["status"] == "in_progress" and again["sections"] == paper["sections"]


def test_late_submissions_are_refused(new_user):
    client = new_user()
    paper = client.post("/api/companies/tcs/tests").json()
    with SessionLocal() as db:  # pretend the test started an hour ago
        attempt = db.get(TestAttempt, paper["id"])
        attempt.started_at = attempt.started_at - timedelta(hours=1)
        db.commit()
    assert client.get(f"/api/tests/{paper['id']}").json()["status"] == "expired"
    assert client.post(f"/api/tests/{paper['id']}/submit", json={"answers": {}}).status_code == 410


def test_you_cannot_see_or_submit_someone_elses_test(new_user):
    owner, intruder = new_user(), new_user()
    paper = owner.post("/api/companies/tcs/tests").json()
    assert intruder.get(f"/api/tests/{paper['id']}").status_code == 404
    assert intruder.post(f"/api/tests/{paper['id']}/submit", json={"answers": {}}).status_code == 404
    assert intruder.get("/api/tests").json() == []


def test_starting_tests_is_rate_limited(new_user):
    client = new_user()
    codes = [client.post("/api/companies/tcs/tests").status_code for _ in range(11)]
    assert codes[:10] == [201] * 10 and codes[10] == 429


def test_deleting_an_account_deletes_its_tests(new_user):
    client = new_user()
    paper = client.post("/api/companies/tcs/tests").json()
    assert client.request("DELETE", "/api/auth/me", json={"password": PASSWORD}).status_code == 204
    with SessionLocal() as db:
        assert db.get(TestAttempt, paper["id"]) is None


# helpers
def company(company_id):
    return next(c for c in COMPANIES if c["id"] == company_id)


def paper_size(company_id):
    return question_count(company(company_id))
