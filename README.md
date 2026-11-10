# Resume Reviewer

A multi-agent AI pipeline that compares a resume with a job description and returns a match score, skill gaps, and rewritten bullet points.

Built with [Google ADK](https://google.github.io/adk-docs/), [LiteLLM](https://docs.litellm.ai/), and a Qwen model hosted on [Groq](https://console.groq.com/).

## How it works

Three agents run in order using ADK's `SequentialAgent`. Each one saves its result to session state, and the next agent reads it.

| Step | Agent | Output |
|---|---|---|
| 1 | `skill_extractor` | Skills, experience, education, and projects from the resume |
| 2 | `match_scorer` | Match score, strengths, gaps, and keywords to add |
| 3 | `resume_rewriter` | Final report with improved bullet points and a tailored summary |

## Features

- Match score from 0 to 100 against any job description
- Clear list of missing skills and keywords
- Before and after rewrites of weak bullet points
- A professional summary tailored to the job
- No invented experience: placeholders like [add metric] are used where numbers are needed

## Project structure

```
resume_reviewer/
├── __init__.py
├── agent.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

## Getting started

**1. Create and activate a virtual environment**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**2. Install dependencies**

```powershell
pip install -r requirements.txt
```

**3. Add your Groq API key**

Create a key at https://console.groq.com/keys and save it in `.env`:

```
GROQ_API_KEY=your-key-here
```

**4. Start the app** from the folder that contains `resume_reviewer`:

```powershell
adk web
```

Open http://127.0.0.1:8000, select `resume_reviewer`, click **+ New Session**, and paste your input.

## Usage

Send the resume and the job description in one message:

```
RESUME:
<paste resume text>

JOB DESCRIPTION:
<paste job description>
```

## Customization

- Change the model in `MODEL_ID` inside `agent.py`.
- Edit any agent's `instruction` to change its focus or tone.
- Add a fourth agent, such as a cover letter writer, to the `sub_agents` list.

## Tech stack

| Component | Purpose |
|---|---|
| Google ADK | Agent framework, `SequentialAgent`, and dev UI |
| LiteLLM | Unified model connector |
| Groq | Fast model hosting |
| Qwen | Language model |

## Security

Keep your `.env` file private. It is already listed in `.gitignore`.


APP LINK - [https://adk-resume-reviewer-im483cdgghtcy8y24fy6t5.streamlit.app/]
