"""
parser.py
Resume PDF parsing using PyMuPDF (fitz).
Extracts raw text and a best-guess candidate name from a resume PDF.
"""

import os
import re

import pymupdf as fitz  # PyMuPDF (using the modern import name; 'fitz' is the deprecated alias)


def extract_text_from_pdf(file_path_or_bytes):
    """
    Extract raw text from a PDF resume.
    Accepts either a file path (str) or raw bytes (e.g. from a Streamlit upload).
    """
    if isinstance(file_path_or_bytes, (bytes, bytearray)):
        doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")
    else:
        doc = fitz.open(file_path_or_bytes)

    text_parts = []
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()

    text = "\n".join(text_parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def guess_candidate_name(text, fallback="Unknown Candidate"):
    """
    Heuristic candidate name extraction.
    Assumes the name sits on one of the first few non-empty lines of the
    resume, is short (1-4 words), has no '@' or digits, and isn't a common
    header like "Resume" or "Curriculum Vitae".
    """
    ignore_words = {
        "resume", "curriculum", "vitae", "cv", "profile", "summary",
        "contact", "email", "phone", "address",
    }

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for line in lines[:8]:
        lower = line.lower()
        if "@" in line or any(ch.isdigit() for ch in line):
            continue
        if any(w in lower for w in ignore_words):
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w[0].isalpha()):
            return line
    return fallback


def parse_resume(file_path_or_bytes, filename="resume.pdf"):
    """
    Full parse of a single resume: returns a dict with raw text and guessed name.
    """
    text = extract_text_from_pdf(file_path_or_bytes)
    name = guess_candidate_name(text, fallback=os.path.splitext(filename)[0])
    return {
        "filename": filename,
        "name": name,
        "text": text,
    }
