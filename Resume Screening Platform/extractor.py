"""
extractor.py
Skill and experience extraction from resume/JD text using spaCy.
"""

import re

import spacy
from spacy.matcher import PhraseMatcher

_nlp = None


def get_nlp():
    """Lazily load the spaCy model (cached for the process lifetime)."""
    global _nlp
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError as exc:
            raise OSError(
                "spaCy model 'en_core_web_sm' not found. "
                "Install it with: python -m spacy download en_core_web_sm"
            ) from exc
    return _nlp


# A reasonably broad default skills database for tech / data / HR-tech roles.
# Extend this list (or load from a CSV/JSON) to cover other domains.
DEFAULT_SKILLS_DB = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "r",
    "go", "rust", "scala", "matlab",
    "django", "flask", "fastapi", "streamlit", "react", "angular", "vue",
    "node.js", "spring boot",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spacy", "nltk", "opencv", "matplotlib", "seaborn",
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "data analysis", "data engineering", "data science",
    "mlops", "llm", "generative ai", "prompt engineering",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "ci/cd", "git", "github", "gitlab",
    "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "snowflake",
    "spark", "hadoop", "airflow", "kafka", "etl",
    "excel", "power bi", "tableau", "looker",
    "rest api", "graphql", "microservices", "linux", "agile", "scrum",
    "html", "css", "sass",
]

_matcher_cache = {}


def build_matcher(skills_db=None):
    """Build (and cache) a PhraseMatcher for the given skills database."""
    nlp = get_nlp()
    skills_db = skills_db or DEFAULT_SKILLS_DB
    cache_key = tuple(sorted(skills_db))
    if cache_key in _matcher_cache:
        return _matcher_cache[cache_key]

    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(skill) for skill in skills_db]
    matcher.add("SKILLS", patterns)
    _matcher_cache[cache_key] = matcher
    return matcher


def extract_skills(text, skills_db=None):
    """
    Returns a sorted list of unique skills found in `text` that appear in
    skills_db (defaults to DEFAULT_SKILLS_DB).
    """
    nlp = get_nlp()
    matcher = build_matcher(skills_db)
    doc = nlp(text)
    matches = matcher(doc)

    found = set()
    for match_id, start, end in matches:
        found.add(doc[start:end].text.lower())
    return sorted(found)


# Matches patterns like "5 years", "5+ years", "5-7 years", "5 yrs experience"
_EXPERIENCE_PATTERNS = [
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)\s*(?:of)?\s*experience",
    r"experience\s*(?:of)?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs|year)",
]


def extract_experience_years(text):
    """
    Heuristic extraction of total years of experience from free text.
    Returns a float (0.0 if nothing is found).
    """
    text_lower = text.lower()
    candidates = []
    for pattern in _EXPERIENCE_PATTERNS:
        for m in re.finditer(pattern, text_lower):
            try:
                candidates.append(float(m.group(1)))
            except ValueError:
                continue

    if candidates:
        return max(candidates)
    return 0.0


def extract_all(text, skills_db=None):
    """Convenience wrapper returning both skills and experience."""
    return {
        "skills": extract_skills(text, skills_db),
        "experience_years": extract_experience_years(text),
    }
