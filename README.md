# 🎙️ AI Interview Coach

An AI-powered mock-interview platform that helps students prepare for campus placements. Answer interview questions **out loud**, and the app transcribes your speech, scores your answer, analyses your delivery (pace, filler words, pauses), reviews your resume for ATS issues, and tracks your progress over time.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?logo=tailwindcss&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2-D71F00)
![Tests](https://img.shields.io/badge/tests-83%20passing-brightgreen)

---

## ✨ Features

| Feature | What it does |
|---|---|
| **Voice practice** | Record answers in the browser with a live waveform; audio is transcribed with **Whisper (large-v3-turbo)** including word-level timestamps. |
| **AI answer scoring** | An LLM evaluates each answer against role-specific criteria and returns structured feedback: scores for relevance, structure and clarity, strengths, improvements and a model sample answer. |
| **Delivery analysis** | Custom speech analysis computes words-per-minute, detects filler words ("um", "like", "you know"), hesitations and long pauses, and produces a delivery score with tips. |
| **Annotated transcript** | Highlights fillers and pauses directly in your transcript so you can see exactly where to improve. |
| **Resume review** | Upload a PDF resume → automated ATS checks (standard headings, action verbs, length, scanned-image detection) plus AI feedback. |
| **Company prep** | Rounds, patterns and practice for **TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini, Amazon, Microsoft, Flipkart and Zoho**. |
| **Aptitude mock tests** | Timed tests on numerical, verbal and reasoning ability with scoring and history. |
| **AI coach chat** | A streaming chat assistant for interview and career questions. |
| **Progress tracking** | Saved sessions, history pages and charts showing how your scores improve. |
| **Roles** | HR, Software Developer, Web Developer and Data Analyst question banks. |

## 🛠️ Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite, JWT (HTTP-only cookies), bcrypt, pypdf, httpx
**AI:** Groq API — Whisper large-v3-turbo (speech-to-text), GPT-OSS 120B (answer evaluation), GPT-OSS 20B (coach chat)
**Frontend:** React 18, React Router 7, Tailwind CSS 4, Recharts, Vite, MediaRecorder API
**DevOps:** Ubuntu + systemd + Caddy (automatic HTTPS), shell scripts for one-command setup, updates and daily DB backups
**Testing:** pytest — 83 tests covering auth, sessions, resume checks, speech analysis, rate limiting, coach and company APIs

## 🏗️ Architecture

```
Browser (React + Vite)
   │  records audio, shows feedback & charts
   ▼
Caddy (HTTPS, serves React build)
   │  /api/*
   ▼
FastAPI backend ──► Groq API (Whisper STT · LLM scoring · coach chat)
   │
   ▼
SQLite (users, sessions, resumes, test attempts, coach messages)
```

## 🔐 Security

- Passwords hashed with **bcrypt**; JWT stored in **HTTP-only cookies**
- Tokens are invalidated automatically when a user changes their password
- **Sliding-window rate limiting** on login, sign-up and AI endpoints
- API keys are read only on the server and never sent to the browser

## 🚀 Run Locally

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # add a SECRET_KEY and a free GROQ_API_KEY
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev                 # http://localhost:5173
```

**Tests**
```bash
cd backend && pytest
```

Deployment to an Ubuntu server is documented in [`deploy/README.md`](deploy/README.md).

## 📁 Project Structure

```
backend/
  app/
    routers/     auth, questions, answers, sessions, resumes, companies, coach
    services/    transcription, evaluation, speech_analysis, resume_checks, coach
    models.py    SQLAlchemy models
  tests/         pytest suite
frontend/
  src/pages/     Practice, Dashboard, History, Resume, Companies, MockTest, Coach …
  src/components AnswerRecorder, LiveWaveform, FeedbackReport, ProgressCharts …
deploy/          setup, update, backup scripts + Caddy & systemd templates
```

## 👤 Author

**Mohammed Saif** — B.Tech CSE
[LinkedIn](https://www.linkedin.com/in/saif-mohammed-939902335/) · [GitHub](https://github.com/MohammedSaif29)
