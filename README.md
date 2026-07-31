# 🎯 Intelligent Resume Screening Platform

An AI-powered resume screening tool that reads PDF resumes, extracts
skills and experience, matches candidates against a job description using
NLP, and ranks them with a clear, explainable score — all through a simple
Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![spaCy](https://img.shields.io/badge/spaCy-NLP-09a3d5)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📌 Overview

Recruiters often receive hundreds of applications for a single job
opening. Manually reading every resume and comparing it against the job
description takes hours of effort and is prone to human error and bias.

This project automates that process:

- Parses every uploaded resume PDF
- Extracts candidate skills and years of experience
- Compares each resume against the job description using NLP
- Produces an explainable match score (0–100) per candidate
- Ranks all candidates and shows exactly which skills matched or are missing

Instead of a black-box "80% match" number, this tool shows **why** a
candidate scored the way they did.

---

## ✨ Features

- 📄 **PDF Resume Parsing** — extracts raw text from any resume PDF
- 🧠 **Skill Extraction** — detects known technical skills using NLP
- ⏳ **Experience Detection** — estimates years of experience from resume text
- 🔍 **Semantic Job Matching** — compares resume and job description by *meaning*, not just keywords
- 📊 **Explainable Scoring** — every score is broken down into matched skills, missing skills, and semantic fit
- 🏆 **Candidate Ranking** — automatically ranks and sorts all uploaded candidates
- 🖥️ **Interactive Dashboard** — built with Streamlit, no separate frontend needed
- 🧩 **Easily Extendable** — add new skills, tune scoring weights, or plug in a custom skills database

---

## 🛠️ Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| Language | [Python 3.11+](https://www.python.org/) | Core programming language |
| PDF Parsing | [PyMuPDF](https://pymupdf.readthedocs.io/) | Extracts text from resume PDFs |
| NLP | [spaCy](https://spacy.io/) | Skill and experience extraction |
| Semantic Matching | [Sentence-Transformers](https://www.sbert.net/) | Compares resume and job description meaning |
| ML Utilities | [scikit-learn](https://scikit-learn.org/) | Normalizes and combines scoring metrics |
| Data Handling | [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) | Tabular data and numerical operations |
| Dashboard | [Streamlit](https://streamlit.io/) | Interactive web UI |

---

## 📂 Project Structure

```
resume-screening-platform/
├── app.py              # Streamlit dashboard (entry point)
├── parser.py            # PDF resume parsing (PyMuPDF)
├── extractor.py           # Skill & experience extraction (spaCy)
├── matcher.py              # Semantic JD matching (Sentence-Transformers)
├── ranking.py               # Candidate scoring & ranking (scikit-learn)
├── requirements.txt
├── resumes/                  # Optional folder for sample resume PDFs
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/resume-screening-platform.git
cd resume-screening-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download the spaCy language model

```bash
python -m spacy download en_core_web_sm
```

> The first run will also auto-download the `all-MiniLM-L6-v2`
> sentence-transformer model (~90MB) — this needs an internet connection
> once.

---

## ▶️ Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

Then open your browser at **http://localhost:8501** and:

1. Paste a job description into the text area
2. Set the required years of experience
3. Upload one or more resume PDFs
4. Click **🔍 Screen Candidates**
5. View the ranked results — click any candidate to see their matched and
   missing skills, experience, and full score breakdown

---

## 🧮 How Scoring Works

Each candidate's final match score (0–100) is a weighted combination of:

| Component | Weight | What It Measures |
|---|---|---|
| Semantic Match | 50% | How closely the resume's overall meaning matches the job description |
| Skill Match | 40% | Fraction of required skills found in the resume |
| Experience Fit | 10% | How well the candidate's experience meets the requirement |

This keeps the score **transparent** — every point can be traced back to
a specific, checkable reason.

---

## 🧩 Extending This Project

- **Add more skills** — edit `DEFAULT_SKILLS_DB` in `extractor.py` to
  cover other domains (marketing, finance, design, etc.)
- **Tune scoring weights** — adjust the `WEIGHTS` dictionary in
  `ranking.py` to prioritize skills, semantic fit, or experience
  differently
- **Improve experience detection** — extend `extract_experience_years()`
  in `extractor.py` to parse work-history date ranges for more accuracy

---

## 🗺️ Roadmap Ideas

- [ ] Support DOCX resumes
- [ ] Export ranked results to CSV/Excel
- [ ] Add a skills database editor in the UI
- [ ] Support multiple job descriptions at once

---

## 🤝 Contributing

Contributions are welcome. Feel free to open an issue or submit a pull
request.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push and open a pull request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙌 Acknowledgements

- [spaCy](https://spacy.io/) for NLP tooling
- [Sentence-Transformers](https://www.sbert.net/) for semantic embeddings
- [Streamlit](https://streamlit.io/) for making dashboards effortless
