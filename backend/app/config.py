"""App settings, read from the .env file.

Secrets (like SECRET_KEY) live in .env, never in code, so they never reach GitHub.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent  # the backend/ folder


class Settings(BaseSettings):
    # Required: the app refuses to start without it.
    # Used to sign login tokens so nobody can forge them.
    secret_key: str

    database_url: str = f"sqlite:///{BACKEND_DIR / 'interview_bot.db'}"
    access_token_expire_minutes: int = 60

    # True in production: the cookie is then only sent over HTTPS.
    cookie_secure: bool = False

    frontend_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env")


settings = Settings()
