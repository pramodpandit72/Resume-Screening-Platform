"""
app.py
Streamlit dashboard for the Intelligent Resume Screening Platform.

Run with:
    streamlit run app.py
"""

import pandas as pd
import streamlit as st

from extractor import extract_experience_years, extract_skills
from matcher import match_skills, semantic_similarity
from parser import parse_resume
from ranking import rank_candidates

st.set_page_config(page_title="Intelligent Resume Screening Platform", layout="wide")

st.title("🎯 Intelligent Resume Screening Platform")
st.caption(
    "Parse resumes, extract skills & experience, match against a job "
    "description, and rank candidates — with explainable scores."
)

# ---------------------------------------------------------------------------
# Input screen
# ---------------------------------------------------------------------------
st.header("1. Input")

col1, col2 = st.columns([1.2, 1])

with col1:
    jd_text = st.text_area(
        "Job Description",
        height=280,
        placeholder=(
            "Paste the job description here (required skills, experience, "
            "responsibilities)..."
        ),
    )

with col2:
    required_years = st.number_input(
        "Required Experience (years)", min_value=0, max_value=30, value=2, step=1
    )
    uploaded_files = st.file_uploader(
        "Upload Resume PDFs", type=["pdf"], accept_multiple_files=True
    )
    if uploaded_files:
        st.write(f"{len(uploaded_files)} resume(s) uploaded")

screen_clicked = st.button("🔍 Screen Candidates", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------
if screen_clicked:
    if not jd_text.strip():
        st.error("Please enter a job description.")
    elif not uploaded_files:
        st.error("Please upload at least one resume PDF.")
    else:
        with st.spinner("Parsing resumes and scoring candidates..."):
            jd_skills = extract_skills(jd_text)

            candidates = []
            for f in uploaded_files:
                file_bytes = f.read()
                parsed = parse_resume(file_bytes, filename=f.name)
                resume_text = parsed["text"]

                resume_skills = extract_skills(resume_text)
                experience_years = extract_experience_years(resume_text)

                semantic_score = semantic_similarity(resume_text, jd_text)
                matched, missing, skill_ratio = match_skills(resume_skills, jd_skills)

                candidates.append({
                    "name": parsed["name"],
                    "filename": parsed["filename"],
                    "skills": resume_skills,
                    "experience_years": experience_years,
                    "semantic_score": semantic_score,
                    "skill_match_ratio": skill_ratio,
                    "matched_skills": matched,
                    "missing_skills": missing,
                })

            ranked = rank_candidates(candidates, required_experience_years=required_years)
            st.session_state["ranked_candidates"] = ranked
            st.session_state["jd_skills"] = jd_skills

# ---------------------------------------------------------------------------
# Result screen
# ---------------------------------------------------------------------------
if "ranked_candidates" in st.session_state:
    ranked = st.session_state["ranked_candidates"]
    jd_skills = st.session_state["jd_skills"]

    st.header("2. Results")

    if jd_skills:
        st.caption("Skills detected in job description: " + ", ".join(jd_skills))
    else:
        st.caption(
            "No known skills detected in the job description — try adding "
            "specific technologies (e.g. Python, SQL, AWS)."
        )

    summary_df = pd.DataFrame([
        {
            "Rank": c["rank"],
            "Candidate": c["name"],
            "File": c["filename"],
            "Match Score (%)": c["match_score"],
            "Experience (yrs)": c["experience_years"],
            "Matched Skills": len(c["matched_skills"]),
            "Missing Skills": len(c["missing_skills"]),
        }
        for c in ranked
    ])
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    st.subheader("Candidate Details")
    for c in ranked:
        with st.expander(f"#{c['rank']} — {c['name']} — {c['match_score']}% match"):
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Match Score", f"{c['match_score']}%")
            col_b.metric("Experience", f"{c['experience_years']} yrs")
            col_c.metric("Rank", f"#{c['rank']}")

            st.markdown(
                "**All Extracted Skills:** "
                + (", ".join(c["skills"]) if c["skills"] else "_None detected_")
            )

            m_col, mi_col = st.columns(2)
            with m_col:
                st.markdown("✅ **Matched Skills**")
                if c["matched_skills"]:
                    st.success(", ".join(c["matched_skills"]))
                else:
                    st.info("No direct skill matches found.")
            with mi_col:
                st.markdown("❌ **Missing Skills**")
                if c["missing_skills"]:
                    st.warning(", ".join(c["missing_skills"]))
                else:
                    st.success("No missing skills — full coverage!")
else:
    st.info(
        "Fill in the job description, upload resumes, and click "
        "**Screen Candidates** to see results."
    )
