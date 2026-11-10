import asyncio
import os
import re

import streamlit as st
from dotenv import load_dotenv
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from google.genai import types
from pypdf import PdfReader

from agent import build_workflow

load_dotenv()

st.set_page_config(page_title="Resume Reviewer", page_icon="📄", layout="wide")


st.markdown(
    """
    <style>
    .hero {
        padding: 1.6rem 1.8rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: #ffffff;
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; color: #ffffff; }
    .hero p { margin: 0.4rem 0 0 0; opacity: 0.92; }
    .stButton > button {
        background: #4f46e5;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.6rem;
        font-weight: 600;
    }
    .stButton > button:hover { background: #4338ca; color: #ffffff; }
    .report-card {
        border: 1px solid rgba(128, 128, 128, 0.35);
        border-radius: 14px;
        padding: 1.2rem 1.5rem;
        margin-top: 0.8rem;
    }
    </style>
    <div class="hero">
        <h1>📄 Resume Reviewer</h1>
        <p>Upload your resume as a PDF and paste a job description to get a match score, skill gaps, and stronger bullet points.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("About")
    st.caption("Upload a text-based PDF resume, paste the job description, and click Review.")
    st.markdown("---")
    st.caption("Built with Google ADK, LiteLLM, Groq, and Streamlit.")



def get_api_key() -> str | None:
    key = os.getenv("GROQ_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None


def read_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = [(page.extract_text() or "") for page in reader.pages]
    return "\n".join(pages).strip()


async def run_review(api_key: str, resume: str, job: str) -> str:
    workflow = build_workflow(api_key)
    app = App(name="agents", root_agent=workflow)
    runner = InMemoryRunner(app=app)

    session = await runner.session_service.create_session(
        app_name=app.name, user_id="web_user"
    )

    prompt = f"RESUME:\n{resume.strip()}\n\nJOB DESCRIPTION:\n{job.strip()}"
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    texts: dict[str, str] = {}
    last = ""
    async for event in runner.run_async(
        user_id="web_user", session_id=session.id, new_message=message
    ):
        if getattr(event, "partial", False):
            continue
        if event.content and event.content.parts:
            text = "".join(
                p.text
                for p in event.content.parts
                if getattr(p, "text", None) and not getattr(p, "thought", False)
            )
            if text.strip():
                texts[event.author] = text
                last = text

    return texts.get("rewriter") or last


def extract_score(report: str) -> int | None:
    match = re.search(r"(?i)match score\D{0,20}(\d{1,3})", report)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 100:
            return score
    return None



left, right = st.columns(2)

resume_text = ""
with left:
    pdf_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
    if pdf_file is not None:
        try:
            resume_text = read_pdf(pdf_file)
        except Exception:
            st.error("Could not read this PDF. Please try a different file.")
        else:
            if resume_text:
                st.success(f"Resume loaded: {len(resume_text.split())} words found.")
                with st.expander("Preview extracted text"):
                    st.text(resume_text[:3000])
            else:
                st.warning(
                    "No text was found in this PDF. It may be a scanned image. "
                    "Please upload a PDF that contains selectable text."
                )

with right:
    job_text = st.text_area(
        "Job description",
        height=320,
        placeholder="Paste the job description here...",
    )

run = st.button("Review my resume")


if run:
    api_key = get_api_key()

    if not resume_text.strip():
        st.warning("Please upload a PDF resume first.")
    elif not job_text.strip():
        st.warning("Please paste the job description.")
    elif not api_key:
        st.error("GROQ_API_KEY was not found. Add it to your .env file and restart the app.")
    else:
        try:
            with st.spinner("Analyzing your resume. This can take up to a minute..."):
                report = asyncio.run(run_review(api_key, resume_text, job_text))
        except Exception as exc:
            st.error(f"Something went wrong: {exc}")
        else:
            if not report:
                st.warning("The model returned an empty answer. Please try again.")
            else:
                score = extract_score(report)
                if score is not None:
                    c1, c2 = st.columns([1, 3])
                    c1.metric("Match score", f"{score}/100")
                    c2.progress(score / 100)

                st.markdown('<div class="report-card">', unsafe_allow_html=True)
                st.markdown(report)
                st.markdown("</div>", unsafe_allow_html=True)

                st.download_button(
                    "Download report (.md)",
                    data=report,
                    file_name="resume_review.md",
                    mime="text/markdown",
                )