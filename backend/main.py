from fastapi import FastAPI
import random

app = FastAPI()

questions = [
    "Tell me about yourself.",
    "What are your strengths and weaknesses?",
    "Why should we hire you?",
    "Explain a project you worked on.",
    "Where do you see yourself in 5 years?"
    "how do you handle stress and pressure?",
    "What is your greatest achievement?",
]

@app.get("/")
def home():
    return {"message": "Interview Bot is running!"}

@app.get("/question")
def get_question():
    return {"question": random.choice(questions)}
@app.get("/tip")
def get_tip():
    return {"tip": random.choice(tips)}