"""
matcher.py
Job description matching using Sentence-Transformers embeddings, plus
skill-level matched/missing comparison.
"""

from sentence_transformers import SentenceTransformer, util

_model = None
_MODEL_NAME = "all-MiniLM-L6-v2"


def get_model():
    """Lazily load the sentence-transformer model (cached for process lifetime)."""
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def semantic_similarity(resume_text, jd_text):
    """
    Returns cosine similarity (0-1) between a resume and a job description,
    computed over sentence embeddings.
    """
    model = get_model()
    embeddings = model.encode([resume_text, jd_text], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    # Clamp to [0, 1] since cosine similarity can dip slightly negative.
    return max(0.0, min(1.0, score))


def match_skills(resume_skills, jd_skills):
    """
    Compares resume skills against JD-required skills.
    Returns (matched, missing, match_ratio) where match_ratio is
    len(matched) / len(jd_skills), i.e. how much of the JD's skill
    requirement the candidate covers.
    """
    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}

    if not jd_set:
        return [], [], 0.0

    matched = sorted(resume_set & jd_set)
    missing = sorted(jd_set - resume_set)
    match_ratio = len(matched) / len(jd_set)
    return matched, missing, match_ratio
