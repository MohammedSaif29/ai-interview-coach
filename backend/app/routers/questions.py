"""Interview roles, questions and tips."""
import random

from fastapi import APIRouter, HTTPException, Query, status

from app.question_bank import ROLES, TIPS

router = APIRouter(tags=["practice"])


@router.get("/roles")
def get_roles():
    return [{"id": role_id, "label": role["label"]} for role_id, role in ROLES.items()]


@router.get("/question")
def get_question(role: str = Query(default="hr")):
    if role not in ROLES:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown interview role.")
    return {"question": random.choice(ROLES[role]["questions"]), "role": role}


@router.get("/tip")
def get_tip():
    return {"tip": random.choice(TIPS)}
