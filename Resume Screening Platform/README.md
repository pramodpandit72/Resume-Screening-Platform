# Intelligent Resume Screening Platform

Parses PDF resumes, extracts skills and experience, matches candidates
against a job description using NLP, and ranks them with an explainable
confidence score — all through a Streamlit dashboard.

## Project Structure

```
resume-screening-platform/
├── app.py             # Streamlit dashboard (entry point)
├── parser.py           # PyMuPDF-based resume PDF parsing
├── extractor.py         # spaCy-based skill & experience extraction
├── matcher.py           # Sentence-Transformers JD matching
├── ranking.py            # scikit-learn based candidate ranking
├── requirements.txt
└── resumes/              # optional folder for sample PDFs
```

## Setup

1. **Create a virtual environment** (Python 3.11+ recommended)

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the spaCy language model** (required by `extractor.py`)

   ```bash
   python -m spacy download en_core_web_sm
   ```

   The first run will also download the `all-MiniLM-L6-v2` sentence-transformer
   model (~90MB) automatically — this requires an internet connection once.

## Run

```bash
streamlit run app.py
```

This opens the dashboard in your browser (default: http://localhost:8501).

## How to Use

1. Paste a job description into the text area.
2. Set the required years of experience (used to weight the ranking).
3. Upload one or more resume PDFs.
4. Click **Screen Candidates**.
5. Review the ranked results table and expand each candidate for:
   - full extracted skill list
   - matched skills (✅ present in both resume and JD)
   - missing skills (❌ required by JD but not found in resume)
   - match score and experience

## How Scoring Works (`ranking.py`)

Each candidate's final match score (0-100) is a weighted blend of:

| Component      | Weight | Description                                             |
|-----------------|--------|-----------------------------------------------------------|
| Semantic match  | 50%    | Cosine similarity between resume and JD embeddings        |
| Skill match     | 40%    | Fraction of JD-required skills found in the resume         |
| Experience fit  | 10%    | How well years of experience meet/exceed the requirement   |

This keeps the score explainable: you can always point to *why* a candidate
ranked where they did (semantic fit, skill coverage, experience).

## Extending

- **Skills database**: edit `DEFAULT_SKILLS_DB` in `extractor.py` to match
  your domain (e.g. add marketing, finance, or design skills).
- **Weights**: tune `WEIGHTS` in `ranking.py` to prioritize skills vs.
  semantic fit vs. experience differently.
- **Experience extraction**: the current approach is regex-based (looks for
  phrases like "5 years experience"). For more accuracy, extend
  `extract_experience_years` in `extractor.py` to parse date ranges from
  work history sections.
