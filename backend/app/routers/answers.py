"""Recorded answers: upload audio, get a transcript back."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.deps import get_current_user
from app.models import User
from app.schemas import TranscriptOut
from app.services.transcription import TranscriptionError, transcribe_audio

router = APIRouter(prefix="/answers", tags=["answers"])

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
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Speech-to-text isn't set up yet. Add GROQ_API_KEY to backend/.env and restart the backend.",
        )

    try:
        return await transcribe_audio(data, audio.filename or "answer.webm", content_type)
    except TranscriptionError as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error))
