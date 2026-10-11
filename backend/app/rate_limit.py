"""Rate limiting: stops one person sending too many requests too fast.

Without it, an attacker could try thousands of passwords per minute, or one user
could burn through our whole AI quota. Each limiter remembers the times of recent
requests per "key" (an IP address, an email, or a user id) and refuses more than
`max_requests` within `per_seconds` with HTTP 429 Too Many Requests.

The counts live in memory, which is fine for one server. A big site running many
servers would keep them in a shared store such as Redis instead.
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

_all_limiters: list["RateLimiter"] = []


class RateLimiter:
    def __init__(self, max_requests: int, per_seconds: int, clock=time.monotonic):
        self.max_requests = max_requests
        self.per_seconds = per_seconds
        self._clock = clock  # swappable, so tests can fake the passing of time
        self._hits: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()  # requests can arrive at the same moment; only one may update counts
        _all_limiters.append(self)

    def _forget_old(self, key: str, now: float) -> deque:
        hits = self._hits[key]
        while hits and now - hits[0] >= self.per_seconds:
            hits.popleft()
        return hits

    def check(self, key: str) -> None:
        """Raises 429 if `key` has used up its requests. Does not count this one."""
        now = self._clock()
        with self._lock:
            hits = self._forget_old(key, now)
            if len(hits) >= self.max_requests:
                wait = int(self.per_seconds - (now - hits[0])) + 1
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"Too many attempts. Try again in {wait} seconds.",
                    headers={"Retry-After": str(wait)},  # tells clients how long to wait
                )

    def record(self, key: str) -> None:
        """Counts one request for `key`."""
        with self._lock:
            self._hits[key].append(self._clock())

    def hit(self, key: str) -> None:
        """Check, then count. The usual way to use a limiter."""
        self.check(key)
        self.record(key)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def reset_all_limiters() -> None:
    """Used by tests, so one test's requests don't affect the next."""
    for limiter in _all_limiters:
        limiter.reset()


def client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


# ---------- The limits used across the app ----------
# Failed logins for one email from one IP: stops password guessing on an account
login_failures = RateLimiter(max_requests=5, per_seconds=60)
# All login attempts from one IP: stops trying one password on many accounts
login_attempts_per_ip = RateLimiter(max_requests=20, per_seconds=60)
# New accounts from one IP
signups_per_ip = RateLimiter(max_requests=5, per_seconds=3600)
# Password changes and account deletions for one user
sensitive_changes = RateLimiter(max_requests=5, per_seconds=900)
# AI calls for one user: protects our free Groq quota
transcriptions = RateLimiter(max_requests=10, per_seconds=60)
evaluations = RateLimiter(max_requests=10, per_seconds=60)
