"""Speech-to-text: sends recorded audio to Groq's Whisper model and gets text back."""
from app.config import settings
from app.services.groq_client import GroqError, groq_post

# Note: we tried sending Whisper a "prompt" full of filler words ("umm, like, uh...")
# to make it keep fillers in the transcript. Testing showed it made Whisper cut
# answers short ("Hello, this is Saif" came back as just "Hello"), so we removed it.
# Whisper drops some "um"s, but it still leaves a gap in the word timestamps where
# the hesitation was. Our speech analysis uses those gaps instead.


class TranscriptionError(Exception):
    """Raised when speech-to-text fails. The message is safe to show users."""


async def transcribe_audio(audio: bytes, filename: str, content_type: str) -> dict:
    """Returns {"transcript", "duration_seconds", "words": [{"word", "start", "end"}]}."""
    try:
        data = await groq_post(
            "/audio/transcriptions",
            files={"file": (filename, audio, content_type)},
            data={
                "model": settings.stt_model,
                "response_format": "verbose_json",  # needed for word timestamps
                "timestamp_granularities[]": ["word", "segment"],
                "language": "en",
                "temperature": "0",
            },
        )
    except GroqError as error:
        if error.status_code not in (None, 401, 429):
            raise TranscriptionError("The speech-to-text service couldn't process this recording. Try recording again.")
        raise TranscriptionError(str(error))

    words = [
        {"word": w["word"].strip(), "start": float(w["start"]), "end": float(w["end"])}
        for w in data.get("words", [])
        if w.get("word", "").strip()
    ]
    return {
        "transcript": data.get("text", "").strip(),
        "duration_seconds": float(data.get("duration", 0)),
        "words": words,
    }
