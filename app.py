"""
app.py
Streamlit dashboard for the Intelligent Resume Screening Platform.

Run with:
    streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # reads GEMINI_API_KEY (and anything else) from a local .env file

from extractor import extract_experience_years, extract_skills
from genai_generator import extract_skills_ai, generate_candidate_summary, generate_interview_questions
from matcher import match_skills, semantic_similarity
from parser import parse_resume
from ranking import rank_candidates

st.set_page_config(page_title="Intelligent Resume Screening Platform", layout="wide")

st.title("🎯 Intelligent Resume Screening Platform")
st.caption(
    "Parse resumes, extract skills & experience, match against a job "
    "description, rank candidates, and generate AI-written recruiter "
    "summaries and interview questions with Gemini."
)

if not os.environ.get("GEMINI_API_KEY"):
    st.warning(
        "⚠️ GEMINI_API_KEY is not set. Scoring and ranking will still "
        "work, but the AI-generated summary/interview-question feature "
        "for each candidate needs a Gemini API key. "
        "Set it with: `export GEMINI_API_KEY='your-key-here'`",
        icon="⚠️",
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
    use_ai_skills = st.checkbox(
        "🔎 AI-enhanced skill detection (catches skills not in the built-in list)",
        value=bool(os.environ.get("GEMINI_API_KEY")),
        help=(
            "When on, Gemini reads the job description and each resume to find "
            "skills/technologies that the fixed keyword list doesn't know about. "
            "Requires GEMINI_API_KEY. Falls back to the built-in list alone if "
            "unavailable or if a call fails."
        ),
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
            jd_skills = set(extract_skills(jd_text))

            ai_unavailable_warning = False
            if use_ai_skills:
                try:
                    jd_skills |= set(extract_skills_ai(jd_text))
                except EnvironmentError:
                    ai_unavailable_warning = True
                except Exception:
                    pass  # AI extraction failed for this text; keep the built-in list results

            jd_skills = sorted(jd_skills)

            candidates = []
            for f in uploaded_files:
                file_bytes = f.read()
                parsed = parse_resume(file_bytes, filename=f.name)
                resume_text = parsed["text"]

                resume_skills = set(extract_skills(resume_text))
                if use_ai_skills:
                    try:
                        resume_skills |= set(extract_skills_ai(resume_text))
                    except EnvironmentError:
                        ai_unavailable_warning = True
                    except Exception:
                        pass  # AI extraction failed for this resume; keep the built-in list results
                resume_skills = sorted(resume_skills)

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

        if ai_unavailable_warning:
            st.info(
                "AI-enhanced skill detection was on but GEMINI_API_KEY isn't set, "
                "so results above use the built-in skill list only.",
                icon="ℹ️",
            )

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

            st.divider()
            st.markdown("### ✨ AI-Generated Insights")
            genai_key = f"genai_{c['rank']}_{c['filename']}"

            if st.button("Generate AI Summary & Interview Questions", key=f"btn_{genai_key}"):
                try:
                    with st.spinner("Asking Gemini to write a summary and interview questions..."):
                        summary = generate_candidate_summary(c, jd_text)
                        questions = generate_interview_questions(c, jd_text)
                        st.session_state[genai_key] = {
                            "summary": summary,
                            "questions": questions,
                        }
                except EnvironmentError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"AI generation failed: {e}")

            if genai_key in st.session_state:
                st.markdown("**🧑‍💼 Recruiter Summary**")
                st.info(st.session_state[genai_key]["summary"])
                st.markdown("**🎤 Suggested Interview Questions**")
                st.write(st.session_state[genai_key]["questions"])
else:
    st.info(
        "Fill in the job description, upload resumes, and click "
        "**Screen Candidates** to see results."
    )
