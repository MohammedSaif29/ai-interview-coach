"""Builds small, real PDF files for tests, so we test with actual PDFs that pypdf reads."""


def make_pdf(lines: list[str], pages: int = 1) -> bytes:
    def escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    }
    kids = []
    for i in range(pages):
        page_id, content_id = 4 + 2 * i, 5 + 2 * i
        kids.append(f"{page_id} 0 R")
        ops = ["BT", "/F1 10 Tf", "13 TL", "40 770 Td"]
        ops += [f"({escape(line)}) Tj T*" for line in lines]
        ops.append("ET")
        stream = "\n".join(ops).encode("latin-1")
        objects[content_id] = b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream"
        objects[page_id] = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_id} 0 R >>"
        ).encode()
    objects[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {pages} >>".encode()

    out = bytearray(b"%PDF-1.4\n")
    offsets = {}
    for number in sorted(objects):
        offsets[number] = len(out)
        out += f"{number} 0 obj\n".encode() + objects[number] + b"\nendobj\n"
    xref_at, size = len(out), max(objects) + 1
    out += f"xref\n0 {size}\n0000000000 65535 f \n".encode()
    for number in range(1, size):
        out += f"{offsets[number]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {size} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    return bytes(out)


GOOD_RESUME = [
    "Saif Mohammed",
    "saif@example.com | +91 98765 43210 | github.com/saif | linkedin.com/in/saif",
    "EDUCATION",
    "B.Tech in Computer Science and Engineering, KL University, 2027, CGPA 8.4",
    "SKILLS",
    "Python, FastAPI, React, JavaScript, SQL, SQLAlchemy, Git, REST APIs, Tailwind CSS",
    "PROJECTS",
    "Interview Bot - AI mock interview platform",
    "- Built a FastAPI backend with JWT authentication, rate limiting and 48 automated tests",
    "- Designed a React frontend with live voice recording, used by 30 students in my college",
    "- Developed speech analysis that measures pace, filler words and pauses from word timestamps",
    "- Integrated Whisper speech-to-text and an LLM that scores answers with structured JSON output",
    "Campus Events App - event discovery for students",
    "- Created a responsive web app listing college events with search and filters",
    "- Improved page load time by 40% by caching API responses and compressing images",
    "EXPERIENCE",
    "Web Development Intern, ABC Technologies, Hyderabad, May to July 2026",
    "- Developed 5 landing pages for client campaigns using React and Tailwind CSS",
    "- Reduced form errors by 25% by adding validation and clearer error messages",
    "- Collaborated with a team of 4 developers using Git, pull requests and code reviews",
    "ACHIEVEMENTS",
    "- Won second place in the college hackathon among 60 teams with an accessibility tool",
    "- Led a workshop on Git and GitHub for 80 first-year students",
    "CERTIFICATIONS",
    "- Python for Everybody, University of Michigan, Coursera",
    "- Responsive Web Design, freeCodeCamp",
] + [
    "- Tested and documented every API endpoint so new team members could start contributing quickly",
] * 6
