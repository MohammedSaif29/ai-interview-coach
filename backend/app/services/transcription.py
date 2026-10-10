"""Speech-to-text: sends recorded audio to Groq's Whisper model and gets text back.

A "service" is code that talks to the outside world (here, another company's API),
kept separate from our routes so it's easy to swap or test.
"""
import httpx

from app.config import settings

GROQ_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

# Note: we tried sending Whisper a "prompt" full of filler words ("umm, like, uh...")
# to make it keep fillers in the transcript. Testing showed it made Whisper cut
# answers short ("Hello, this is Saif" came back as just "Hello"), so we removed it.
# Whisper drops some "um"s, but it still leaves a gap in the word timestamps where
# the hesitation was. Our speech analysis uses those gaps instead.


class TranscriptionError(Exception):
    """Raised when the speech-to-text service fails. The message is safe to show users."""


async def transcribe_audio(audio: bytes, filename: str, content_type: str) -> dict:
    """Returns {"transcript", "duration_seconds", "words": [{"word", "start", "end"}]}."""
    try:
        # async: while waiting for Groq, the server can keep handling other requests
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                files={"file": (filename, audio, content_type)},
                data={
                    "model": settings.stt_model,
                    "response_format": "verbose_json",  # needed for word timestamps
                    "timestamp_granularities[]": ["word", "segment"],
                    "language": "en",
                    "temperature": "0",
                },
            )
    except httpx.HTTPError:
        raise TranscriptionError("Couldn't reach the speech-to-text service. Check your internet connection.")

    if response.status_code == 401:
        raise TranscriptionError("The speech-to-text API key is invalid. Check GROQ_API_KEY in backend/.env.")
    if response.status_code == 429:
        raise TranscriptionError("Too many transcriptions right now. Wait a minute and try again.")
    if response.status_code != 200:
        raise TranscriptionError("The speech-to-text service couldn't process this recording. Try recording again.")

    data = response.json()
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
