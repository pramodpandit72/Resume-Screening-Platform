# Let's Understand Your Project — Simple Explanation

Hi! Let's go through your project together, slowly, like I'm explaining it
to you in a classroom. No technical background needed. I'll explain what
each thing is, why we needed it, and how it all works together.

---

## First, What Problem Are We Solving?

Imagine you are an HR manager. You post a job. You get 500 resumes.

You cannot read all 500 resumes one by one. It will take too long.

So we built a program that:

- reads every resume for you
- checks what skills each person has
- checks how much experience each person has
- compares each resume with the job description
- gives every person a score out of 100
- shows you the best candidates first

That's it. That is the whole project, in one sentence.

Now let's understand how we built this, piece by piece.

---

## Step 1: We Needed a Language to Write the Program In

We used **Python**.

Think of Python like the language we are writing our instructions in —
just like you'd write instructions in English or Hindi. Python is popular
for this kind of project because a lot of ready-made tools already exist
for it. We don't have to build everything from zero. We can just borrow
tools that other smart people already built.

---

## Step 2: We Needed to Open PDF Resumes and Read the Text

A resume comes as a PDF file. But a computer doesn't automatically know
how to "read" a PDF like a human does. A PDF is really just a picture of a
page layout.

So we used a tool called **PyMuPDF**.

Think of PyMuPDF like a pair of eyes. Its only job is: open the PDF, look
at it, and copy out all the plain text so the rest of our program can
work with it.

This is used in the file called `parser.py`.

---

## Step 3: We Needed to Understand the Text, Not Just Read It

Now we have plain text from the resume. But just having text isn't enough.
We need to find specific skill words inside it — like "Python", "AWS", or
"Machine Learning."

For this, we used a tool called **spaCy**.

Think of spaCy like a highlighter pen that knows what to highlight. If we
tell it "look for these skill names," it will scan the whole resume and
mark every skill it finds. It's smart enough to know that "Machine
Learning" is one skill, not two separate random words.

spaCy is also used to guess how many years of experience someone has, by
looking for phrases like "5 years experience."

This is used in the file called `extractor.py`.

---

## Step 4: We Needed to Compare the Resume With the Job Description

This is the tricky part. A resume might say "built REST APIs." The job
description might say "developed backend services." These are different
words but they mean almost the same thing. If we just compared exact
words, we would miss this match completely.

So we used a tool called **Sentence-Transformers**.

Think of it like this: this tool reads a sentence and turns it into a
"fingerprint" made of numbers, based on what the sentence *means*, not
just what words it uses. Then we compare the job description's fingerprint
with the resume's fingerprint. If the fingerprints are close to each
other, it means the meanings are close too — even if the exact words are
different.

We also separately check: does the resume contain the exact skills the
job description is asking for? This gives us a clear list of matched
skills and missing skills.

This is used in the file called `matcher.py`.

---

## Step 5: We Needed to Turn All These Numbers Into One Final Score

By this point, for every candidate we have three separate pieces of
information:

1. How close their resume "means" to the job description (a number)
2. How many required skills they actually have (a number)
3. How much experience they have (a number)

These three numbers are on different scales, so we can't just add them
directly — that would be unfair. So we used a small tool from a library
called **scikit-learn**, specifically something called **MinMaxScaler**.

Think of MinMaxScaler like a teacher grading on a curve. It takes all the
raw numbers and squishes them fairly into the same 0-to-1 range, so no
single number can unfairly dominate the others just because it happens to
be numerically bigger.

Once everything is on the same scale, we combine them using fixed weights:

- 50% comes from how well the meaning matches
- 40% comes from how many required skills they have
- 10% comes from experience

This gives us one final score out of 100 for each person. Then we simply
sort everyone from highest score to lowest score. That's the ranking.

This is used in the file called `ranking.py`.

---

## Step 6: We Needed a Screen Where Someone Can Actually Use This

All the steps above happen behind the scenes. But someone still needs a
simple screen to paste the job description, upload resumes, and press a
button.

For this, we used **Streamlit**.

Think of Streamlit like a tool that turns plain Python code into a real
website — without needing to know web design at all. We just write things
like "show a text box here" or "show a button here" in Python, and
Streamlit turns it into an actual webpage.

This is the file called `app.py`. It is the "control room" — it calls all
the other files in the right order and shows the results.

---

## Step 7: We Needed to Show the Results Neatly

Once every candidate has a score, we want to show it as a clean table —
like a spreadsheet, with columns for Name, Score, Experience, and so on.

For this, we used **pandas**.

Think of pandas like a spreadsheet tool inside Python. It organizes all
our results into neat rows and columns, and Streamlit knows how to display
that table nicely on the screen.

---

## Step 8 (New): We Added Real Generative AI

Everything above only *reads* and *measures* text that already exists.
None of it actually *writes* anything new. That's an important detail —
tools like spaCy and Sentence-Transformers are called **NLP (Natural
Language Processing)**, not **GenAI (Generative AI)**, because they don't
create new content.

So we added a new file: **`genai_generator.py`**. This one is different.
It connects to **Gemini** (an AI model made by Google) through an API,
and asks it to actually *write* two brand-new things for every candidate:

1. A short, 2-3 sentence recruiter summary explaining why this person is
   or isn't a good fit — written fresh, not copied from the resume.
2. A list of tailored interview questions, based on what skills the
   candidate already has and which ones they're missing.

Think of the difference like this: earlier tools were like a very
thorough highlighter and calculator — they find and measure things that
are already there. Gemini is like an assistant who actually reads the
notes and then *writes you something new* — a summary, in their own
words, and a set of custom interview questions no one typed anywhere.

This is what makes it a true GenAI project — not just an NLP project.

To use this feature, you need a free Gemini API key from
**aistudio.google.com/apikey**, saved as an environment variable called
`GEMINI_API_KEY`. If it's missing, everything else in the app (parsing,
matching, scoring, ranking) still works fine — you just won't see the AI
summary/interview-question button work until the key is added.

---

## Step 9 (New): We Made Skill-Finding Smarter Too

Remember Step 3, where spaCy finds skills by checking text against a
fixed list of words we typed in (`DEFAULT_SKILLS_DB`)? That approach has
one weakness: if a skill isn't on the list, it can never be found — even
if it's written clearly on the resume.

For example, if a job description asks for "Snowpark" and that word was
never added to our list, the old version of the program would act like
that word doesn't exist at all.

We fixed this by giving Gemini the same job — but without a fixed list.
Instead of "check if these exact words appear," we now also ask Gemini:
**"read this text and tell me what skills you see in it."** Since Gemini
already understands language broadly, it can recognize a skill it's
never been specifically told about, the same way a human recruiter would
recognize "Snowpark" as a data tool even if nobody wrote it on a
checklist beforehand.

Here's how the two methods now work together:

1. First, spaCy quickly checks the fixed list (fast, free, always works).
2. Then, if AI-enhanced detection is turned on and a Gemini key is set,
   Gemini also reads the same text and adds any skills it notices that
   weren't already found.
3. Both results are combined into one final skill list — nothing is lost,
   and nothing is missed just because it wasn't typed into a list ahead
   of time.

If the Gemini key isn't available, or the request fails for any reason,
the program quietly falls back to just the fixed-list result — so the
app never breaks, it just becomes slightly less thorough at
skill-finding.

This lives in a new function called `extract_skills_ai()` inside
`genai_generator.py`, and there's a checkbox in the app itself —
**"AI-enhanced skill detection"** — that lets you turn this behavior on
or off.

---

## One More Small Helper: numpy

**numpy** works quietly in the background. It helps scikit-learn do its
math correctly when it's squishing numbers into the 0-to-1 range. You will
almost never notice it directly, but it's the engine running underneath.

---

## Now Let's Walk Through the Whole Journey, Start to Finish

Let's say you paste this job description:
*"Looking for a Data Engineer with Python, SQL, AWS, 3+ years experience."*

And you upload 3 resumes.

Here is exactly what happens when you click the "Screen Candidates"
button:

1. **PyMuPDF** opens each resume PDF and pulls out the plain text.
2. **spaCy** scans that text and finds skill words like "python," "sql,"
   "aws" — and also tries to find a number like "3 years experience."
3. **Sentence-Transformers** compares the meaning of the whole resume to
   the meaning of the whole job description, and gives a similarity score.
4. We also directly compare skill lists: which required skills does this
   person have, and which are they missing?
5. **scikit-learn's MinMaxScaler** fairly balances all these numbers, and
   we combine them into one final score out of 100.
6. This repeats for all 3 resumes.
7. Everyone is sorted from highest score to lowest score — this becomes
   the ranking.
8. **Streamlit + pandas** display everything neatly: a table showing
   Rank, Name, Score, Experience — and if you click on someone, you can
   see exactly which skills matched and which ones are missing.

---

## Why This Isn't a "Mystery Black Box"

A lot of AI tools just say "this person is 80% match" and give no reason.
We didn't want that.

In our project, the final score is made of three clear, checkable pieces:

- meaning-match (does the resume generally sound related to the job?)
- skill-match (an exact list you can literally read — matched vs missing)
- experience-match (a simple, plain comparison of years)

Because we know exactly how the score was built, we can always explain
*why* someone got 78% instead of 60%. Nothing is hidden.

---

## Simple Recap Table

| Tool | What it's like | What it actually does |
|---|---|---|
| Python | The language | Everything is written using it |
| PyMuPDF | A pair of eyes | Reads the PDF and pulls out text |
| spaCy | A smart highlighter | Finds skill words and experience numbers in text |
| Sentence-Transformers | A "meaning fingerprint" maker | Compares how similar two texts mean, not just how similar the words look |
| scikit-learn (MinMaxScaler) | A fair grading curve | Makes sure different numbers can be combined fairly |
| numpy | The engine under the hood | Helps do the math quickly and correctly |
| pandas | A spreadsheet tool | Organizes results into a neat table |
| Streamlit | The website builder | Turns our Python code into a usable webpage/dashboard |

That's the whole project. Nothing magical — just several small, honest
tools, each doing one clear job, connected together in the right order.
