"""Database connection.

We use SQLite (a single file, nothing to install) for now. Because everything goes
through SQLAlchemy, switching to PostgreSQL later only means changing DATABASE_URL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite needs this flag because FastAPI may use the connection from different threads.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Every database table (model) inherits from this."""


def get_db():
    """Gives each request its own database session and always closes it afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
