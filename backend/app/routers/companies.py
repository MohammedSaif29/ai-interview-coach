"""Company prep: hiring patterns for each company, and timed mock tests in their style.

📘 Security idea: the correct answers NEVER leave the server until the test is submitted.
The browser only gets the questions and shuffled options, and the server does the marking.
Otherwise anyone could open the browser's network tab and read the answers.
"""
import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.aptitude_bank import QUESTIONS_BY_ID, questions_in
from app.companies import COMPANIES, COMPANIES_BY_ID, LAST_CHECKED, level_for, question_count
from app.database import get_db
from app.deps import get_current_user
from app.models import TestAttempt, User
from app.rate_limit import test_starts
from app.schemas import TestSubmit, as_utc

router = APIRouter(tags=["companies"])

# Extra time allowed after the timer ends, for slow networks. After that the test expires.
GRACE_SECONDS = 60


def get_company(company_id: str) -> dict:
    company = COMPANIES_BY_ID.get(company_id)
    if company is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Company not found.")
    return company


def get_own_attempt(attempt_id: int, user: User, db: Session) -> TestAttempt:
    attempt = db.get(TestAttempt, attempt_id)
    if attempt is None or attempt.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Test not found.")
    return attempt


def deadline(attempt: TestAttempt) -> datetime:
    return as_utc(attempt.started_at) + timedelta(seconds=attempt.time_limit_seconds)


def attempt_status(attempt: TestAttempt) -> str:
    if attempt.submitted_at is not None:
        return "submitted"
    if datetime.now(timezone.utc) > deadline(attempt) + timedelta(seconds=GRACE_SECONDS):
        return "expired"
    return "in_progress"


def mock_info(company: dict) -> dict:
    return {
        "minutes": company["mock"]["minutes"],
        "question_count": question_count(company),
        "sections": [{"name": s["name"], "count": sum(s["pick"].values())} for s in company["mock"]["sections"]],
        "coding_note": company["coding_note"],
    }


def attempt_summary(attempt: TestAttempt) -> dict:
    company = COMPANIES_BY_ID.get(attempt.company_id, {"name": attempt.company_id, "levels": []})
    return {
        "id": attempt.id,
        "company_id": attempt.company_id,
        "company_name": company["name"],
        "score": attempt.score,
        "correct": attempt.correct_count,
        "total": len(attempt.questions),
        "level": level_for(company, attempt.score)["label"] if company["levels"] else None,
        "submitted_at": as_utc(attempt.submitted_at),
    }


def submitted_attempts(db: Session, user_id: int, company_id: str | None = None) -> list[TestAttempt]:
    query = select(TestAttempt).where(TestAttempt.user_id == user_id, TestAttempt.submitted_at.is_not(None))
    if company_id:
        query = query.where(TestAttempt.company_id == company_id)
    return list(db.scalars(query.order_by(TestAttempt.submitted_at.desc(), TestAttempt.id.desc())))


# ---------- Companies ----------

@router.get("/companies")
def list_companies(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    best: dict[str, int] = {}
    for attempt in submitted_attempts(db, user.id):
        best[attempt.company_id] = max(best.get(attempt.company_id, 0), attempt.score)
    return [
        {
            "id": c["id"], "name": c["name"], "full_name": c["full_name"], "kind": c["kind"], "exam": c["exam"],
            "roles": [r["name"] for r in c["roles"]],
            "round_count": len(c["rounds"]),
            "minutes": c["mock"]["minutes"],
            "question_count": question_count(c),
            "best_score": best.get(c["id"]),
        }
        for c in COMPANIES
    ]


@router.get("/companies/{company_id}")
def company_detail(company_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = get_company(company_id)
    detail = {key: company[key] for key in
              ("id", "name", "full_name", "kind", "exam", "summary", "roles", "rounds", "focus", "tips", "careers_url", "sources")}
    detail["levels"] = [{"min": level["min"], "label": level["label"]} for level in company["levels"]]
    detail["mock"] = mock_info(company)
    detail["last_checked"] = LAST_CHECKED
    detail["attempts"] = [attempt_summary(a) for a in submitted_attempts(db, user.id, company_id)[:10]]
    return detail


# ---------- Mock tests ----------

def pick_questions(company: dict) -> list[dict]:
    """Random questions for each section. A question is never used twice in one test."""
    used: set[str] = set()
    picked = []
    for section in company["mock"]["sections"]:
        for category, count in section["pick"].items():
            pool = [q for q in questions_in(category) if q["id"] not in used]
            for question in random.sample(pool, count):
                used.add(question["id"])
                order = [0, 1, 2, 3]
                random.shuffle(order)  # option 0 in the bank is the correct one; this hides where it lands
                picked.append({"id": question["id"], "section": section["name"], "order": order})
    return picked


def options_shown(question: dict, order: list[int]) -> list[str]:
    options = [question["correct"], *question["wrong"]]
    return [options[i] for i in order]


def test_paper(attempt: TestAttempt, company: dict) -> dict:
    """What the student sees while taking the test. No answers, no explanations."""
    sections: list[dict] = []
    for item in attempt.questions:
        question = QUESTIONS_BY_ID[item["id"]]
        if not sections or sections[-1]["name"] != item["section"]:
            sections.append({"name": item["section"], "questions": []})
        sections[-1]["questions"].append({
            "id": question["id"], "text": question["text"], "code": question["code"],
            "options": options_shown(question, item["order"]),
        })
    return {
        "id": attempt.id,
        "status": "in_progress",
        "company_id": company["id"],
        "company_name": company["name"],
        "exam": company["exam"],
        "time_limit_seconds": attempt.time_limit_seconds,
        "started_at": as_utc(attempt.started_at),
        "deadline": deadline(attempt),
        "sections": sections,
    }


def test_result(attempt: TestAttempt, company: dict) -> dict:
    """The marked test: scores, level estimate, and every question with the right answer explained."""
    answers = attempt.answers or {}
    review = []
    for item in attempt.questions:
        question = QUESTIONS_BY_ID[item["id"]]
        review.append({
            "id": question["id"], "section": item["section"], "text": question["text"], "code": question["code"],
            "options": options_shown(question, item["order"]),
            "chosen": answers.get(question["id"]),
            "correct": item["order"].index(0),  # where the correct option ended up after shuffling
            "explain": question["explain"],
        })
    submitted = as_utc(attempt.submitted_at)
    return {
        **attempt_summary(attempt),
        "status": "submitted",
        "exam": company["exam"],
        "level": level_for(company, attempt.score),
        "sections": attempt.section_scores,
        "time_taken_seconds": min(int((submitted - as_utc(attempt.started_at)).total_seconds()), attempt.time_limit_seconds),
        "time_limit_seconds": attempt.time_limit_seconds,
        "auto_submitted": attempt.auto_submitted,
        "review": review,
    }


@router.post("/companies/{company_id}/tests", status_code=status.HTTP_201_CREATED)
def start_test(company_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = get_company(company_id)
    test_starts.hit(f"user:{user.id}")
    attempt = TestAttempt(
        user_id=user.id,
        company_id=company_id,
        questions=pick_questions(company),
        time_limit_seconds=company["mock"]["minutes"] * 60,
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return test_paper(attempt, company)


@router.get("/tests")
def list_tests(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return [attempt_summary(a) for a in submitted_attempts(db, user.id)[:50]]


@router.get("/tests/{attempt_id}")
def get_test(attempt_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempt = get_own_attempt(attempt_id, user, db)
    company = get_company(attempt.company_id)
    state = attempt_status(attempt)
    if state == "submitted":
        return test_result(attempt, company)
    if state == "in_progress":
        return test_paper(attempt, company)  # e.g. the page was refreshed mid-test
    return {"id": attempt.id, "status": "expired", "company_id": company["id"], "company_name": company["name"]}


@router.post("/tests/{attempt_id}/submit")
def submit_test(attempt_id: int, body: TestSubmit, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    attempt = get_own_attempt(attempt_id, user, db)
    company = get_company(attempt.company_id)
    state = attempt_status(attempt)
    if state == "submitted":
        raise HTTPException(status.HTTP_409_CONFLICT, "This test has already been submitted.")
    if state == "expired":
        raise HTTPException(status.HTTP_410_GONE, "Time ran out for this test. Start a new one.")

    # Only keep answers to questions that are actually in this test
    asked = {item["id"] for item in attempt.questions}
    answers = {qid: choice for qid, choice in body.answers.items() if qid in asked}

    sections: dict[str, dict] = {}
    correct_total = 0
    for item in attempt.questions:
        right = answers.get(item["id"]) is not None and item["order"][answers[item["id"]]] == 0
        correct_total += right
        section = sections.setdefault(item["section"], {"name": item["section"], "correct": 0, "total": 0})
        section["total"] += 1
        section["correct"] += right

    attempt.answers = answers
    attempt.correct_count = correct_total
    attempt.score = round(100 * correct_total / len(attempt.questions))
    attempt.section_scores = list(sections.values())
    attempt.auto_submitted = body.auto_submitted
    attempt.submitted_at = datetime.now(timezone.utc)
    db.commit()
    return test_result(attempt, company)
