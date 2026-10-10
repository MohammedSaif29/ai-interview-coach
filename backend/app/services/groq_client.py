"""One place for calling Groq's API (used for speech-to-text and for answer scoring).

Keeping this in one file means every Groq call handles errors the same way,
and the API key is only read here.
"""
import logging

import httpx

from app.config import settings

# Messages logged here appear in the terminal where uvicorn is running.
# Users see a friendly message; the technical details stay on the server.
logger = logging.getLogger("uvicorn.error")

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqError(Exception):
    """A Groq call failed. The message is safe to show to users."""

    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}  # Groq's error body, for code that wants to inspect it


async def groq_post(path: str, *, timeout: float = 60, **request_kwargs) -> dict:
    """POST to a Groq endpoint and return the JSON response.

    request_kwargs are passed to httpx: json=... for normal requests,
    files=... and data=... for file uploads.
    """
    try:
        # async: while waiting for Groq, the server can keep handling other requests
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}{path}",
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
                **request_kwargs,
            )
    except httpx.TimeoutException:
        raise GroqError("The AI service took too long to respond. Try again.")
    except httpx.HTTPError:
        raise GroqError("Couldn't reach the AI service. Check your internet connection.")

    details = {}
    if response.status_code != 200:
        # Log Groq's own explanation for us developers (never includes the API key)
        logger.warning("Groq %s failed with %s: %s", path, response.status_code, response.text[:600])
        try:
            details = response.json()
        except ValueError:
            details = {}

    if response.status_code == 401:
        raise GroqError("The Groq API key is invalid. Check GROQ_API_KEY in backend/.env.", 401)
    if response.status_code == 429:
        raise GroqError("Too many requests to the AI service right now. Wait a minute and try again.", 429)
    if response.status_code == 413:
        raise GroqError("This request is too large for the AI service's free limits. Try a shorter answer.", 413)
    if response.status_code != 200:
        raise GroqError("The AI service couldn't process this request. Try again.", response.status_code, details)

    return response.json()
