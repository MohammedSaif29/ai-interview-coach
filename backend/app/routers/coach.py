"""The AI coach chat: message history, sending a message (streamed reply), clearing the chat."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.deps import get_current_user
from app.models import CoachMessage, User
from app.rate_limit import coach_messages
from app.schemas import CoachMessageIn, CoachMessageOut
from app.services import coach
from app.services.groq_client import GroqError

router = APIRouter(prefix="/coach", tags=["coach"])

CUT_OFF_NOTE = "\n\n_(The answer was cut off. Try asking again.)_"


@router.get("/messages", response_model=list[CoachMessageOut])
def get_messages(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    latest = db.scalars(
        select(CoachMessage)
        .where(CoachMessage.user_id == user.id)
        .order_by(CoachMessage.created_at.desc(), CoachMessage.id.desc())
        .limit(50)
    ).all()
    return list(reversed(latest))  # oldest first, like a chat


@router.post("/messages")
async def send_message(data: CoachMessageIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    coach_messages.hit(f"user:{user.id}")
    if not settings.groq_api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AI features aren't set up yet. Add GROQ_API_KEY to backend/.env and restart the backend.",
        )

    question = CoachMessage(user_id=user.id, role="user", content=data.content.strip())
    db.add(question)
    db.commit()

    recent = db.scalars(
        select(CoachMessage)
        .where(CoachMessage.user_id == user.id)
        .order_by(CoachMessage.created_at.desc(), CoachMessage.id.desc())
        .limit(coach.HISTORY_MESSAGES)
    ).all()
    history = [{"role": m.role, "content": m.content} for m in reversed(recent)]
    messages = coach.build_messages(coach.build_student_context(user, db), history)

    # Wait for the FIRST piece before replying. If the AI fails right away, we can still
    # send a proper error status. (Once streaming starts, the status is already "200 OK".)
    reply = coach.stream_chat(messages)
    try:
        first_piece = await anext(reply)
    except (GroqError, StopAsyncIteration) as error:
        db.delete(question)  # don't leave an unanswered question in the history
        db.commit()
        message = str(error) if isinstance(error, GroqError) else "The coach didn't reply. Try again."
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, message)

    user_id = user.id

    async def stream_and_save():
        pieces = [first_piece]
        yield first_piece
        try:
            async for piece in reply:
                pieces.append(piece)
                yield piece
        except GroqError:
            pieces.append(CUT_OFF_NOTE)
            yield CUT_OFF_NOTE
        # The request's database session is closed by now, so open a fresh one to save the reply
        with SessionLocal() as save_db:
            save_db.add(CoachMessage(user_id=user_id, role="assistant", content="".join(pieces)))
            save_db.commit()

    return StreamingResponse(
        stream_and_save(),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # don't buffer: send pieces right away
    )


@router.delete("/messages", status_code=status.HTTP_204_NO_CONTENT)
def clear_messages(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.execute(delete(CoachMessage).where(CoachMessage.user_id == user.id))
    db.commit()
