"""
genai_generator.py
Generative AI features using Google's Gemini API.

This is the "Gen" part of the project: everything else in this codebase
(parser.py, extractor.py, matcher.py, ranking.py) only READS and MEASURES
existing text. This file is different — it asks Gemini to WRITE brand-new
content that didn't exist before, and also to intelligently FIND things
that a fixed keyword list would miss:

  1. A short, plain-English recruiter summary of each candidate's fit
  2. A tailored set of interview questions for each candidate
  3. Skill extraction that isn't limited to a hard-coded list — Gemini
     reads the actual text and identifies real skills/technologies

Requires a Gemini API key. Get one free at https://aistudio.google.com/apikey
and set it as an environment variable before running the app:

    export GEMINI_API_KEY="your-key-here"      # macOS / Linux
    setx GEMINI_API_KEY "your-key-here"         # Windows

Requires the google-genai package:
    pip install google-genai
"""

import json
import os
import re

from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads GEMINI_API_KEY from a local .env file, if present

_client = None
_MODEL = "gemini-2.5-flash"  # fast and inexpensive; swap for gemini-2.5-pro if you want higher quality


def get_client():
    """Lazily create (and cache) the Gemini API client."""
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY environment variable is not set.\n"
                "Get a free key from https://aistudio.google.com/apikey and set it, e.g.:\n"
                "  export GEMINI_API_KEY='your-key-here'"
            )
        _client = genai.Client(api_key=api_key)
    return _client


def extract_skills_ai(text, max_skills=40):
    """
    Uses Gemini to identify technical skills, tools, technologies,
    platforms, programming languages, and frameworks mentioned in `text` —
    WITHOUT being limited to any fixed keyword list. This catches things
    that extractor.py's hard-coded DEFAULT_SKILLS_DB would otherwise miss
    (e.g. a niche tool the list author never thought to add).

    Returns a sorted list of lowercase skill strings. Returns an empty
    list (never raises) if the AI response can't be parsed, so callers
    can safely fall back to the spaCy-based extraction alone.
    """
    client = get_client()

    prompt = f"""Extract a list of technical skills, tools, technologies, \
platforms, programming languages, and frameworks mentioned in the text \
below. Only include genuine technical skills — do NOT include soft \
skills like "communication" or "teamwork", and do NOT include job \
titles or company names.

Return ONLY a JSON array of lowercase strings, nothing else — no \
markdown, no explanation. Example output:
["python", "aws", "snowpark", "looker studio"]

Return at most {max_skills} items.

Text:
{text}"""

    response = client.models.generate_content(model=_MODEL, contents=prompt)
    raw = response.text.strip()

    # Gemini sometimes wraps JSON in ```json ... ``` fences despite instructions — strip those.
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        return []

    skills = {
        item.strip().lower()
        for item in parsed
        if isinstance(item, str) and item.strip()
    }
    return sorted(skills)


def generate_candidate_summary(candidate, jd_text):
    """
    Asks Gemini to write a short (2-3 sentence) recruiter-facing summary
    explaining why this candidate is, or isn't, a good fit for the role.
    """
    client = get_client()

    prompt = f"""You are helping a recruiter quickly understand a job candidate.

Job description:
{jd_text}

Candidate: {candidate['name']}
Match score: {candidate['match_score']}/100
Matched skills: {', '.join(candidate['matched_skills']) or 'none'}
Missing skills: {', '.join(candidate['missing_skills']) or 'none'}
Years of experience: {candidate['experience_years']}

Write a short, 2-3 sentence recruiter-facing summary of this candidate's \
fit for the role. Be specific and factual. Do not invent details that \
aren't given above."""

    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
    )
    return response.text.strip()


def generate_interview_questions(candidate, jd_text, num_questions=5):
    """
    Asks Gemini to write a set of tailored interview questions for this
    specific candidate — a mix of questions that verify their matched
    skills and questions that probe their skill gaps.
    """
    client = get_client()

    prompt = f"""You are helping a recruiter prepare for a candidate interview.

Job description:
{jd_text}

Candidate: {candidate['name']}
Matched skills: {', '.join(candidate['matched_skills']) or 'none'}
Missing skills: {', '.join(candidate['missing_skills']) or 'none'}
Years of experience: {candidate['experience_years']}

Write {num_questions} targeted interview questions for this candidate. \
Include a mix of:
- questions that verify their claimed matched skills
- questions that probe their gaps in the missing skills
- one question about their overall experience relevant to this role

Return ONLY a numbered list of questions, nothing else."""

    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
    )
    return response.text.strip()
