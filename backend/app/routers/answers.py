"""Recorded answers: upload audio to get a transcript, then get AI feedback on it."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.deps import get_current_user
from app.models import User
from app.routers.questions import ROLES, role_label
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
    user: User = Depends(get_current_user),  # login required: stops strangers using our API quota
):
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
    result["analysis"] = analyse_speech(result["words"], result["transcript"], result["duration_seconds"])
    return result


@router.post("/evaluate", response_model=Evaluation)
async def evaluate(data: EvaluateRequest, user: User = Depends(get_current_user)):
    if data.role not in ROLES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Unknown interview role.")
    if len(data.transcript.split()) < 5:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Your answer is too short to score. Record at least a few sentences.",
        )
    if not settings.groq_api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, NOT_SET_UP)

    try:
        return await evaluate_answer(data.question.strip(), data.transcript.strip(), role_label(data.role))
    except EvaluationError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))
