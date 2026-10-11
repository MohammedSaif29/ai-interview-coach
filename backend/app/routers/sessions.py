"""Saved practice sessions: history, one session's details, progress stats, delete.

AUTHORIZATION: every query filters by the logged-in user's id, so nobody can read
or delete another person's sessions, even by guessing ids in the URL.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import PracticeSession, User
from app.schemas import SessionDetail, SessionSummary, StatsOut

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_own_session(session_id: int, user: User, db: Session) -> PracticeSession:
    session = db.get(PracticeSession, session_id)
    if session is None or session.user_id != user.id:
        # 404, not 403: we don't even admit that someone else's session exists
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found.")
    return session


@router.get("", response_model=list[SessionSummary])
def list_sessions(
    limit: int = Query(default=20, ge=1, le=100),  # PAGINATION: send results in pages
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        select(PracticeSession)
        .where(PracticeSession.user_id == user.id)
        .order_by(PracticeSession.created_at.desc(), PracticeSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.scalars(query).all()


# Note: this route must come BEFORE "/{session_id}", or "stats" would be read as an id
@router.get("/stats", response_model=StatsOut)
def session_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    mine = PracticeSession.user_id == user.id
    # SQL does the counting and averaging. AVG skips sessions that weren't scored (NULL).
    total, average_content, average_delivery = db.execute(
        select(
            func.count(PracticeSession.id),
            func.avg(PracticeSession.content_score),
            func.avg(PracticeSession.delivery_score),
        ).where(mine)
    ).one()

    latest = db.scalars(
        select(PracticeSession).where(mine).order_by(PracticeSession.created_at.desc(), PracticeSession.id.desc()).limit(20)
    ).all()

    trend = [
        {
            "id": s.id,
            "created_at": s.created_at,
            "content_score": s.content_score,
            "delivery_score": s.delivery_score,
            # Same rule as the delivery score: very short answers count as half a minute
            "fillers_per_minute": round(s.filler_count / max(s.speaking_seconds / 60, 0.5), 1),
            "words_per_minute": s.words_per_minute,
        }
        for s in reversed(latest)  # oldest first, so charts read left to right
    ]
    return {
        "total_sessions": total,
        "average_content": round(average_content, 1) if average_content is not None else None,
        "average_delivery": round(average_delivery, 1) if average_delivery is not None else None,
        "trend": trend,
    }


@router.get("/{session_id}", response_model=SessionDetail)
def get_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_own_session(session_id, user, db)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(get_own_session(session_id, user, db))
    db.commit()
