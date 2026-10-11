"""Tests for accounts: login, rate limits, settings, and security.

Run them from the backend folder with:   pytest
"""
from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import PASSWORD


def login(client, email, password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# ---------- Basics ----------

def test_signup_logs_you_in(new_user):
    me = new_user()
    assert me.get("/api/auth/me").status_code == 200


def test_wrong_password_gives_the_same_message_as_unknown_email(new_user):
    me = new_user()
    browser = TestClient(app)
    wrong_password = login(browser, me.email, "wrong-password-1")
    unknown_email = login(browser, "nobody@test.com", "wrong-password-1")
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()  # attackers learn nothing


def test_logout(new_user):
    me = new_user()
    me.post("/api/auth/logout")
    assert me.get("/api/auth/me").status_code == 401


# ---------- Rate limiting ----------

def test_too_many_failed_logins_are_blocked(new_user):
    me = new_user()
    attacker = TestClient(app)
    for _ in range(5):
        assert login(attacker, me.email, "guess-guess-1").status_code == 401
    blocked = login(attacker, me.email, "guess-guess-1")
    assert blocked.status_code == 429
    assert "Retry-After" in blocked.headers
    # Even the right password is refused until the wait is over
    assert login(attacker, me.email).status_code == 429


def test_successful_logins_are_not_counted_as_failures(new_user):
    me = new_user()
    browser = TestClient(app)
    for _ in range(8):
        assert login(browser, me.email).status_code == 200


def test_ai_calls_are_limited_per_user(new_user):
    me = new_user()
    audio = {"audio": ("a.webm", b"0" * 5000, "audio/webm")}
    form = {"role": "hr", "question": "Tell me about yourself."}
    for _ in range(10):
        assert me.post("/api/answers/transcribe", files=audio, data=form).status_code == 200
    assert me.post("/api/answers/transcribe", files=audio, data=form).status_code == 429


# ---------- Settings ----------

def test_change_name(new_user):
    me = new_user()
    response = me.patch("/api/auth/me", json={"name": "  Saif  "})
    assert response.status_code == 200
    assert response.json()["name"] == "Saif"


def test_change_password_needs_the_current_password(new_user):
    me = new_user()
    response = me.post("/api/auth/change-password", json={"current_password": "not-it-123", "new_password": "brandnew123"})
    assert response.status_code == 400


def test_changing_password_logs_out_other_devices(new_user):
    laptop = new_user()
    phone = TestClient(app)
    assert login(phone, laptop.email).status_code == 200

    response = laptop.post("/api/auth/change-password", json={"current_password": PASSWORD, "new_password": "brandnew123"})
    assert response.status_code == 204

    assert laptop.get("/api/auth/me").status_code == 200  # this browser got a fresh token
    assert phone.get("/api/auth/me").status_code == 401   # the old token stopped working
    assert login(TestClient(app), laptop.email).status_code == 401  # old password rejected
    assert login(TestClient(app), laptop.email, "brandnew123").status_code == 200


def test_delete_account_needs_the_password(new_user):
    me = new_user()
    response = me.request("DELETE", "/api/auth/me", json={"password": "not-it-123"})
    assert response.status_code == 400
    assert me.get("/api/auth/me").status_code == 200  # still here


def test_deleting_an_account_deletes_its_sessions(new_user):
    alice, bob = new_user(), new_user()
    form = {"role": "hr", "question": "Tell me about yourself."}
    audio = {"audio": ("a.webm", b"0" * 5000, "audio/webm")}
    alice_session = alice.post("/api/answers/transcribe", files=audio, data=form).json()["session_id"]
    bob.post("/api/answers/transcribe", files=audio, data=form)

    assert alice.request("DELETE", "/api/auth/me", json={"password": PASSWORD}).status_code == 204

    assert alice.get("/api/auth/me").status_code == 401
    assert login(TestClient(app), alice.email).status_code == 401
    assert bob.get(f"/api/sessions/{alice_session}").status_code == 404
    assert len(bob.get("/api/sessions").json()) == 1  # Bob's own session is untouched


# ---------- Security headers ----------

def test_security_headers_on_every_response():
    response = TestClient(app).get("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
