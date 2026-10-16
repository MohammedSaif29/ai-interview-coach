"""One place for calling Groq's API (speech-to-text, answer scoring, and the coach chat).

Keeping this in one file means every Groq call handles errors the same way,
and the API key is only read here.
"""
import json
import logging
from collections.abc import AsyncIterator

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


def _headers() -> dict:
    return {"Authorization": f"Bearer {settings.groq_api_key}"}


def _error_for_response(path: str, status_code: int, text: str) -> GroqError:
    """Turns a failed Groq response into a friendly GroqError (and logs the details)."""
    # Log Groq's own explanation for us developers (never includes the API key)
    logger.warning("Groq %s failed with %s: %s", path, status_code, text[:600])
    try:
        details = json.loads(text)
    except ValueError:
        details = {}

    if status_code == 401:
        return GroqError("The Groq API key is invalid. Check GROQ_API_KEY in backend/.env.", 401)
    if status_code == 429:
        return GroqError("Too many requests to the AI service right now. Wait a minute and try again.", 429)
    if status_code == 413:
        return GroqError("This request is too large for the AI service's free limits. Try a shorter message.", 413)
    return GroqError("The AI service couldn't process this request. Try again.", status_code, details)


async def groq_post(path: str, *, timeout: float = 60, **request_kwargs) -> dict:
    """POST to a Groq endpoint and return the JSON response.

    request_kwargs are passed to httpx: json=... for normal requests,
    files=... and data=... for file uploads.
    """
    try:
        # async: while waiting for Groq, the server can keep handling other requests
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(f"{GROQ_BASE_URL}{path}", headers=_headers(), **request_kwargs)
    except httpx.TimeoutException:
        raise GroqError("The AI service took too long to respond. Try again.")
    except httpx.HTTPError:
        raise GroqError("Couldn't reach the AI service. Check your internet connection.")

    if response.status_code != 200:
        raise _error_for_response(path, response.status_code, response.text)
    return response.json()


async def groq_stream_chat(body: dict) -> AsyncIterator[str]:
    """STREAMING: yields the reply a few words at a time, as the model writes it.

    Groq sends "Server-Sent Events": lines like  data: {...json...}  and finally
    data: [DONE]. Each JSON piece holds the next few characters of the answer.
    """
    path = "/chat/completions"
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60, connect=10)) as client:
            async with client.stream(
                "POST", f"{GROQ_BASE_URL}{path}", headers=_headers(), json={**body, "stream": True}
            ) as response:
                if response.status_code != 200:
                    text = (await response.aread()).decode(errors="replace")
                    raise _error_for_response(path, response.status_code, text)
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data = line[len("data: "):]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        piece = json.loads(data)["choices"][0].get("delta", {}).get("content")
                    except (ValueError, KeyError, IndexError):
                        continue
                    if piece:
                        yield piece
    except httpx.TimeoutException:
        raise GroqError("The AI service took too long to respond. Try again.")
    except httpx.HTTPError:
        raise GroqError("Couldn't reach the AI service. Check your internet connection.")
