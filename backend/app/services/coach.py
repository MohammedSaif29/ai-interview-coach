"""The AI coach: a chat guide for interviews and placements that knows the student's progress.

Every request sends the model three things:
1. SYSTEM_PROMPT: who the coach is and how it should answer
2. A short summary of the student's real practice data (build_student_context)
3. The recent conversation
"""
from collections.abc import AsyncIterator

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import PracticeSession, User
from app.question_bank import role_label
from app.services.groq_client import groq_stream_chat

HISTORY_MESSAGES = 10  # how many recent messages the coach sees (keeps requests small)

SYSTEM_PROMPT = """You are the coach inside Interview Bot, an app where university students in India
practise job interviews out loud and get scored on content and delivery.

You are a friendly, practical mentor for interviews and campus placements. You help with:
answering interview questions (including the STAR method), HR and technical rounds,
aptitude tests, coding-interview strategy, communication and confidence, resumes,
the campus placement process, and making study plans.

How to answer:
- Be concise: usually under 180 words, unless the student asks for detail or a plan.
- Be specific and actionable. Short paragraphs or bullet points. Use **bold** sparingly.
- Speak to the student as "you", in simple, clear English.
- Use the student's practice data (given below) when it's relevant, for example to say
  what to work on next. Never invent sessions, scores or details that aren't in the data.
- Suggest the app's features when useful: the Practice page (spoken answers for HR round,
  Software developer, Web developer and Data analyst), History, and the Dashboard charts.
- Company exam patterns, cut-offs and role packages change every year. Share what is generally
  known, say it may have changed, and suggest checking the company's official careers page.
- If asked about something unrelated to careers, studies or interviews, answer briefly
  and kindly, then steer back to preparation.
- If the student sounds very stressed or low, be warm, suggest a short break, and suggest
  talking to a friend, family member or the college counsellor."""


def build_student_context(user: User, db: Session) -> str:
    """A short, factual summary of the student's practice, for the coach to use."""
    mine = PracticeSession.user_id == user.id
    total, avg_content, avg_delivery = db.execute(
        select(
            func.count(PracticeSession.id),
            func.avg(PracticeSession.content_score),
            func.avg(PracticeSession.delivery_score),
        ).where(mine)
    ).one()

    lines = [f"Student's name: {user.name}."]
    if not total:
        lines.append("They haven't recorded any practice sessions yet.")
        return "\n".join(lines)

    summary = f"Practice so far: {total} session{'s' if total != 1 else ''}."
    if avg_content is not None:
        summary += f" Average content score {avg_content:.1f}/10."
    summary += f" Average delivery score {avg_delivery:.1f}/10."
    lines.append(summary)
    lines.append("Most recent sessions, newest first:")

    recent = db.scalars(
        select(PracticeSession).where(mine).order_by(PracticeSession.created_at.desc(), PracticeSession.id.desc()).limit(5)
    ).all()
    for s in recent:
        content = f"content {s.content_score}/10" if s.content_score is not None else "content not scored"
        line = (
            f'- {role_label(s.role)}: "{s.question}" ({content}, delivery {s.delivery_score}/10, '
            f"{s.words_per_minute} words per minute, {s.filler_count} filler words, {s.pause_count} pauses)"
        )
        improvements = (s.feedback or {}).get("improvements") or []
        if improvements:
            line += f". Feedback to improve: {improvements[0]}"
        lines.append(line)
    return "\n".join(lines)


def build_messages(context: str, history: list[dict]) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"The student's practice data:\n{context}"},
        *history,
    ]


def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    """Streams the coach's reply. Kept as its own function so tests can replace it."""
    return groq_stream_chat({
        "model": settings.chat_model,
        "messages": messages,
        "temperature": 0.6,
        "max_completion_tokens": 1000,  # keeps requests within the free plan's per-minute limit
        "reasoning_effort": "low",
        "include_reasoning": False,
    })
