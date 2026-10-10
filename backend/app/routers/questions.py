"""Interview questions and tips."""
import random

from fastapi import APIRouter

router = APIRouter(tags=["practice"])

QUESTIONS = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?",
    "Explain a project you worked on.",
    "Where do you see yourself in 5 years?",
    "How do you handle stress and pressure?",
    "What is your greatest achievement?",
]

TIPS = [
    "Maintain eye contact and be confident.",
    "Speak slowly and clearly.",
    "Use the STAR method: Situation, Task, Action, Result.",
    "Research the company before the interview.",
]


@router.get("/question")
def get_question():
    return {"question": random.choice(QUESTIONS)}


@router.get("/tip")
def get_tip():
    return {"tip": random.choice(TIPS)}
