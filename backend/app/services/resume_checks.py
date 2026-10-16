"""Reading a resume PDF, and the automatic "ATS" checks.

ATS = Applicant Tracking System: software many companies use to filter resumes before a
person reads them. These checks are plain rules written in Python, not AI, so every
result can be explained (and is tested in tests/test_resume_checks.py).
"""
import re
from io import BytesIO

from pypdf import PdfReader

MAX_PAGES = 5           # a resume is 1-2 pages; more than 5 is probably the wrong file
MIN_TEXT_CHARS = 200    # less text than this usually means a scanned image

ACTION_VERBS = {
    "achieved", "analysed", "analyzed", "automated", "built", "collaborated", "configured",
    "coordinated", "created", "delivered", "deployed", "designed", "developed", "engineered",
    "established", "implemented", "improved", "increased", "integrated", "launched", "led",
    "managed", "mentored", "migrated", "optimised", "optimized", "organised", "organized",
    "presented", "reduced", "researched", "solved", "streamlined", "tested", "trained", "won", "wrote",
}
STANDARD_HEADINGS = {
    "education", "skills", "technical skills", "projects", "academic projects", "experience",
    "work experience", "internship", "internships", "certifications", "achievements",
    "summary", "objective", "profile", "activities", "extracurricular activities",
}


class ResumeReadError(Exception):
    """The PDF couldn't be used. The message is safe to show users."""


def extract_resume_text(pdf_bytes: bytes) -> tuple[str, int]:
    """Returns (text, number of pages)."""
    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        if reader.is_encrypted:
            raise ResumeReadError("This PDF is password-protected. Save a copy without a password and upload that.")
        page_count = len(reader.pages)
        if page_count > MAX_PAGES:
            raise ResumeReadError(f"This PDF has {page_count} pages. A resume should be 1 or 2 pages.")
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except ResumeReadError:
        raise
    except Exception:
        # Uploaded files can be broken in endless ways; any failure means "can't read it"
        raise ResumeReadError("We couldn't open this PDF. Try exporting it again from Word or Google Docs.")

    text = re.sub(r"[ \t]+", " ", text)          # squash repeated spaces
    text = re.sub(r"\n\s*\n+", "\n", text).strip()  # drop empty lines
    if len(text) < MIN_TEXT_CHARS:
        raise ResumeReadError(
            "We couldn't find enough text in this PDF. If it's a scanned image or a design exported "
            "as pictures (common with Canva), export it as a text PDF from Word or Google Docs."
        )
    return text, page_count


def _check(check_id: str, label: str, passed: bool, tip: str) -> dict:
    return {"id": check_id, "label": label, "passed": passed, "tip": tip}


def run_checks(text: str, page_count: int) -> list[dict]:
    """The automatic checks. Each one: what we looked for, whether it passed, and a tip."""
    lower = text.lower()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    word_count = len(re.findall(r"[A-Za-z][A-Za-z'+#.]*", text))

    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = any(10 <= len(re.sub(r"\D", "", m)) <= 13 for m in re.findall(r"\+?\d[\d\s()-]{8,16}\d", text))

    headings = {
        re.sub(r"[^a-z ]", "", line.lower()).strip() for line in lines
    } & STANDARD_HEADINGS

    # Results with numbers: percentages, "30+", or a number followed by a countable thing
    quantified = re.findall(
        r"\b\d+(?:\.\d+)?\s?%|\b\d+\+|\b\d+\s?(?:x|k|users|students|people|members|customers|clients|"
        r"downloads|teams|hours|days|weeks|projects|apps|pages|tests|times)\b",
        lower,
    )

    def first_word(line: str) -> str:
        return re.sub(r"^[^A-Za-z]+", "", line).split(" ")[0].lower()

    verb_lines = sum(1 for line in lines if first_word(line) in ACTION_VERBS)
    first_person = len(re.findall(r"\b(?:i|me|my)\b", lower))

    if word_count < 250:
        words_tip = "Your resume looks short. Add details to your projects, skills and achievements."
    else:
        words_tip = "Your resume is quite long. Cut older or less relevant details so the best parts stand out."

    return [
        _check("contact", "Email and phone number", bool(email) and phone,
               "Put your email and phone number at the top, so recruiters can contact you."),
        _check("links", "LinkedIn or GitHub link", "linkedin.com" in lower or "github.com" in lower,
               "Add your LinkedIn and GitHub links. For tech roles, GitHub shows your real work."),
        _check("length", "One page", page_count == 1,
               "Students and freshers should keep their resume to one page."),
        _check("headings", "Standard section headings", len(headings) >= 3,
               "Use clear headings like Education, Skills, Projects and Experience, so ATS software can read your resume."),
        _check("numbers", "Results with numbers", len(quantified) >= 2,
               "Show your impact with numbers, like “used by 30 students” or “cut load time by 40%”."),
        _check("verbs", "Points start with action verbs", verb_lines >= 3,
               "Start bullet points with strong verbs like Built, Designed, Led or Improved."),
        _check("voice", "No “I” or “my”", first_person <= 2,
               "Resumes usually skip “I” and “my”. Write “Built a web app”, not “I built a web app”."),
        _check("words", "Right amount of text (250–700 words)", 250 <= word_count <= 700, words_tip),
    ]


def count_words(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'+#.]*", text))
