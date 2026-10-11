"""Tests for the rate limiter itself. A fake clock lets us 'wait' without sleeping."""
import pytest
from fastapi import HTTPException

from app.rate_limit import RateLimiter


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_allows_up_to_the_limit_then_blocks():
    limiter = RateLimiter(max_requests=3, per_seconds=60, clock=FakeClock())
    for _ in range(3):
        limiter.hit("saif")
    with pytest.raises(HTTPException) as blocked:
        limiter.hit("saif")
    assert blocked.value.status_code == 429
    assert "Retry-After" in blocked.value.headers


def test_each_key_has_its_own_count():
    limiter = RateLimiter(max_requests=1, per_seconds=60, clock=FakeClock())
    limiter.hit("alice")
    limiter.hit("bob")  # not blocked by Alice's request


def test_old_requests_expire():
    clock = FakeClock()
    limiter = RateLimiter(max_requests=2, per_seconds=60, clock=clock)
    limiter.hit("saif")
    limiter.hit("saif")
    clock.now += 61  # a minute later
    limiter.hit("saif")  # allowed again


def test_check_does_not_count():
    limiter = RateLimiter(max_requests=1, per_seconds=60, clock=FakeClock())
    limiter.check("saif")
    limiter.check("saif")  # still fine: check() only looks, record() counts
    limiter.record("saif")
    with pytest.raises(HTTPException):
        limiter.check("saif")
