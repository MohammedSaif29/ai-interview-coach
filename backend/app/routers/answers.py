"""Recorded answers: upload audio to get a transcript (saved as a session),
then get AI feedback on that session."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.models import PracticeSession, User
from app.question_bank import is_known_question, role_label
from app.schemas import EvaluateRequest, Evaluation, TranscriptOut
from app.services.evaluation import EvaluationError, evaluate_answer
from app.services.speech_analysis import analyse_speech
from app.services.transcription import TranscriptionError, transcribe_audio

router = APIRouter(prefix="/answers", tags=["answers"])

NOT_SET_UP = "AI features aren't set up yet. Add GROQ_API_KEY to backend/.env and restart the backend."

MAX_BYTES = 10 * 1024 * 1024  # 10 MB, roughly 10+ minutes of compressed speech
MIN_BYTES = 2_000             # anything smaller is basically silence

# Formats browsers record in (Chrome/Firefox: webm or ogg, Safari: mp4)
ALLOWED_TYPES = {
    "audio/webm", "audio/ogg", "audio/mp4", "audio/mpeg",
    "audio/wav", "audio/x-wav", "audio/m4a", "audio/x-m4a", "video/webm",
}


@router.post("/transcribe", response_model=TranscriptOut)
async def transcribe_answer(
    audio: UploadFile = File(...),
    role: str = Form(...),       # Form(...): sent alongside the file in the same upload
    question: str = Form(...),
    user: User = Depends(get_current_user),  # login required: stops strangers using our API quota
    db: Session = Depends(get_db),
):
    if not is_known_question(role, question):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "That question isn't in our question bank.")

    # "audio/webm;codecs=opus" -> "audio/webm"
    content_type = (audio.content_type or "").split(";")[0].strip().lower()
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "That file isn't a supported audio recording.")

    # Read at most MAX_BYTES + 1, so a huge upload can't fill the server's memory
    data = await audio.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "The recording is too large (max 10 MB).")
    if len(data) < MIN_BYTES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The recording is empty or too short. Record your answer again.")

    if not settings.groq_api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, NOT_SET_UP)

    try:
        result = await transcribe_audio(data, audio.filename or "answer.webm", content_type)
    except TranscriptionError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))

    # Our own analysis of HOW they spoke: instant, no AI involved
    analysis = analyse_speech(result["words"], result["transcript"], result["duration_seconds"])
    result["analysis"] = analysis
    result["session_id"] = None

    # Save it. The SERVER calculated these numbers, so users can't fake their scores.
    if result["transcript"]:
        session = PracticeSession(
            user_id=user.id,
            role=role,
            question=question,
            transcript=result["transcript"],
            duration_seconds=result["duration_seconds"],
            speaking_seconds=analysis["speaking_seconds"],
            words_per_minute=analysis["words_per_minute"],
            filler_count=analysis["filler_count"],
            pause_count=analysis["hesitation_count"] + analysis["long_pause_count"],
            delivery_score=analysis["delivery_score"],
            analysis=analysis,
        )
        db.add(session)
        db.commit()
        result["session_id"] = session.id

    return result


@router.post("/evaluate", response_model=Evaluation)
async def evaluate(data: EvaluateRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Only the owner's sessions can be found. Someone else's id looks like "not found".
    session = db.get(PracticeSession, data.session_id)
    if session is None or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found.")

    # Already scored? Return the saved feedback instead of paying for another AI call
    if session.feedback:
        return session.feedback

    if len(session.transcript.split()) < 5:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Your answer is too short to score. Record at least a few sentences.",
        )
    if not settings.groq_api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, NOT_SET_UP)

    try:
        feedback = await evaluate_answer(session.question, session.transcript, role_label(session.role))
    except EvaluationError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))

    session.content_score = feedback.overall
    session.feedback = feedback.model_dump()
    db.commit()
    return feedback
