"""The question bank: interview roles, their questions, and tips.

Kept in its own file so routes (questions.py, answers.py) and saved sessions
can all use it without importing each other.
"""

# Each role has its own question bank. "label" is what users see.
ROLES = {
    "hr": {
        "label": "HR round",
        "questions": [
            "Tell me about yourself.",
            "What are your strengths and weaknesses?",
            "Why should we hire you?",
            "Where do you see yourself in 5 years?",
            "How do you handle stress and pressure?",
            "What is your greatest achievement?",
            "Tell me about a time you worked in a team.",
            "Tell me about a time you failed. What did you learn?",
            "Why do you want to work at our company?",
        ],
    },
    "software": {
        "label": "Software developer",
        "questions": [
            "Explain a project you worked on and your role in it.",
            "Tell me about a difficult bug you fixed. How did you find it?",
            "What is the difference between a process and a thread?",
            "How would you explain object-oriented programming to a beginner?",
            "What happens when you type a URL into a browser and press Enter?",
            "How do you make sure your code is easy for others to understand?",
            "Tell me about a time you had to learn a new technology quickly.",
            "What is the difference between SQL and NoSQL databases? When would you use each?",
        ],
    },
    "web": {
        "label": "Web developer",
        "questions": [
            "Walk me through a website or web app you built.",
            "What is the difference between the frontend and the backend?",
            "How does a REST API work? Give an example from your own work.",
            "How would you make a slow web page load faster?",
            "What is authentication, and how would you add login to a web app?",
            "What is responsive design, and how do you build for mobile?",
            "Explain what React state is and why it matters.",
        ],
    },
    "data": {
        "label": "Data analyst",
        "questions": [
            "Tell me about a data project you worked on, from question to result.",
            "How would you handle missing or messy data in a dataset?",
            "Explain the difference between mean and median. When does it matter?",
            "How would you explain a technical finding to a non-technical manager?",
            "What is the difference between correlation and causation?",
            "Which tools do you use for data analysis, and why?",
            "Tell me about a time data changed your mind about something.",
        ],
    },
}

TIPS = [
    "Maintain eye contact and be confident.",
    "Speak slowly and clearly.",
    "Use the STAR method: Situation, Task, Action, Result.",
    "Research the company before the interview.",
    "Pause for a second before answering. It sounds more confident than 'um'.",
    "End each answer with the result or what you learned.",
]


def role_label(role: str) -> str:
    return ROLES[role]["label"] if role in ROLES else ROLES["hr"]["label"]


def is_known_question(role: str, question: str) -> bool:
    """True only for questions we actually asked. Stops anyone saving made-up data."""
    return role in ROLES and question in ROLES[role]["questions"]
