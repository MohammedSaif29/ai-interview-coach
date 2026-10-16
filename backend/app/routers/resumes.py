"""Resume review: upload a PDF, get automatic checks + an AI review, see past reviews,
and get practice questions about your own resume."""
import random

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Resume, User
from app.question_bank import RESUME_ROLE, RESUME_TARGETS, target_label
from app.rate_limit import resume_reviews
from app.schemas import ResumeOut, ResumeSummary
from app.services.resume_checks import ResumeReadError, count_words, extract_resume_text, run_checks
from app.services.resume_review import ReviewError, review_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_BYTES = 5 * 1024 * 1024  # 5 MB is plenty for a 1-2 page resume


def latest_resume(db: Session, user_id: int) -> Resume | None:
    return db.scalar(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc(), Resume.id.desc()).limit(1)
    )


def get_own_resume(resume_id: int, user: User, db: Session) -> Resume:
    resume = db.get(Resume, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found.")
    return resume


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    target_role: str = Form(default="any"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if target_role not in RESUME_TARGETS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown target role.")

    data = await file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "That file is too large (max 5 MB).")
    # Check the file's first bytes, not just its name: every real PDF starts with "%PDF-"
    if not data.startswith(b"%PDF-"):
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Upload your resume as a PDF file.")

    resume_reviews.hit(f"user:{user.id}")
    if not settings.groq_api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AI features aren't set up yet. Add GROQ_API_KEY to backend/.env and restart the backend.",
        )

    try:
        text, page_count = extract_resume_text(data)
    except ResumeReadError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error))

    checks = run_checks(text, page_count)
    try:
        review = await review_resume(text, target_label(target_role), checks)
    except ReviewError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))

    resume = Resume(
        user_id=user.id,
        filename=(file.filename or "resume.pdf").replace("\\", "/").split("/")[-1][:150],
        target_role=target_role,
        page_count=page_count,
        word_count=count_words(text),
        text=text,
        checks=checks,
        review=review.model_dump(),
        score=review.overall_score,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeSummary])
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc(), Resume.id.desc())
    ).all()


# Must come BEFORE "/{resume_id}", or "question" would be read as an id
@router.get("/question")
def resume_question(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """A random interview question about the student's latest resume (for the Practice page)."""
    resume = latest_resume(db, user.id)
    questions = (resume.review.get("interview_questions") if resume else None) or []
    if not questions:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload your resume first to get questions about it.")
    return {"question": random.choice(questions), "role": RESUME_ROLE}


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_own_resume(resume_id, user, db)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(get_own_resume(resume_id, user, db))
    db.commit()
