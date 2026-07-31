"""
ranking.py
Candidate ranking using scikit-learn.

Combines semantic similarity, skill match ratio, and experience into a
single normalized, explainable match score (0-100), then ranks candidates.
"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Weights for the final explainable score. Should sum to 1.0.
WEIGHTS = {
    "semantic": 0.5,      # how well the resume text semantically matches the JD
    "skill_match": 0.4,   # fraction of JD-required skills the candidate has
    "experience": 0.1,    # how well experience meets/exceeds the requirement
}


def _normalize(values):
    """Min-max normalize a list of numbers to [0, 1]. Handles edge cases."""
    arr = np.array(values, dtype=float).reshape(-1, 1)
    if len(arr) <= 1 or np.ptp(arr) == 0:
        return np.ones(len(arr)) if len(arr) else arr.flatten()
    scaler = MinMaxScaler()
    return scaler.fit_transform(arr).flatten()


def rank_candidates(candidates, required_experience_years=0):
    """
    candidates: list of dicts, each containing:
        name, semantic_score (0-1), skill_match_ratio (0-1),
        experience_years, matched_skills, missing_skills
    required_experience_years: JD-required years. If > 0, the experience
        component is `min(candidate_years / required_years, 1.0)`.
        If 0, experience is instead normalized relative to the other
        candidates in the batch.

    Returns the same list, sorted by final score descending, each augmented
    with 'match_score' (0-100) and 'rank' (1-indexed).
    """
    if not candidates:
        return []

    exp_values = [c["experience_years"] for c in candidates]
    norm_exp_relative = _normalize(exp_values)

    for i, c in enumerate(candidates):
        semantic = c["semantic_score"]
        skill_match = c["skill_match_ratio"]

        if required_experience_years and required_experience_years > 0:
            exp_component = min(c["experience_years"] / required_experience_years, 1.0)
        else:
            exp_component = norm_exp_relative[i]

        final = (
            WEIGHTS["semantic"] * semantic
            + WEIGHTS["skill_match"] * skill_match
            + WEIGHTS["experience"] * exp_component
        )
        c["match_score"] = round(final * 100, 2)

    ranked = sorted(candidates, key=lambda c: c["match_score"], reverse=True)
    for i, c in enumerate(ranked, start=1):
        c["rank"] = i

    return ranked
