"""Tests for reading resume PDFs and the automatic ATS checks (plain rules, no AI)."""
import pytest

from app.services.resume_checks import ResumeReadError, extract_resume_text, run_checks
from tests.pdf_helper import GOOD_RESUME, make_pdf


def checks_by_id(text, pages=1):
    return {c["id"]: c["passed"] for c in run_checks(text, pages)}


def test_reads_text_from_a_real_pdf():
    text, pages = extract_resume_text(make_pdf(GOOD_RESUME))
    assert pages == 1
    assert "Interview Bot" in text
    assert "saif@example.com" in text


def test_a_strong_resume_passes_every_check():
    text, pages = extract_resume_text(make_pdf(GOOD_RESUME))
    assert all(checks_by_id(text, pages).values()), checks_by_id(text, pages)


def test_scanned_or_empty_pdfs_are_explained():
    with pytest.raises(ResumeReadError, match="enough text"):
        extract_resume_text(make_pdf(["Saif"]))


def test_broken_files_are_explained():
    with pytest.raises(ResumeReadError, match="couldn't open"):
        extract_resume_text(b"%PDF-1.4 this is not really a pdf")


def test_too_many_pages_is_explained():
    with pytest.raises(ResumeReadError, match="pages"):
        extract_resume_text(make_pdf(GOOD_RESUME, pages=6))


def test_missing_contact_details_and_links():
    text = "\n".join(line for line in GOOD_RESUME if "@" not in line)
    result = checks_by_id(text)
    assert result["contact"] is False
    assert result["links"] is False


def test_two_pages_fails_the_one_page_check():
    assert checks_by_id("\n".join(GOOD_RESUME), pages=2)["length"] is False


def test_numbers_and_action_verbs_are_counted():
    weak = "EDUCATION\nSKILLS\nPROJECTS\nWorked on a website.\nDid some coding.\nMade an app."
    result = checks_by_id(weak)
    assert result["numbers"] is False
    assert result["verbs"] is False
    assert result["headings"] is True


def test_first_person_writing_is_flagged():
    text = "\n".join(GOOD_RESUME) + "\nI built my app. I love my work. I am a fast learner."
    assert checks_by_id(text)["voice"] is False
