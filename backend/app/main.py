"""Entry point: creates the app and plugs in all the routers.

Run from the backend/ folder with:  uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (imported so SQLAlchemy knows about our tables)
from app.config import settings
from app.database import Base, engine
from app.routers import answers, auth, coach, companies, questions, resumes, sessions

# Create any missing tables. (Later we'll switch to Alembic migrations.)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Interview Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,  # allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_headers(request, call_next):
    """MIDDLEWARE: runs on every request. These headers tell browsers to be stricter."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")  # don't guess file types
    response.headers.setdefault("X-Frame-Options", "DENY")            # can't be embedded in other sites
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response


# Every route lives under /api, e.g. /api/auth/login, /api/question
app.include_router(auth.router, prefix="/api")
app.include_router(questions.router, prefix="/api")
app.include_router(answers.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(coach.router, prefix="/api")
app.include_router(resumes.router, prefix="/api")
app.include_router(companies.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
