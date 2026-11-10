from google.adk import Agent, Workflow
from google.adk.models.lite_llm import LiteLlm

MODEL_ID = "groq/openai/gpt-oss-20b"


def make_model(api_key: str | None = None) -> LiteLlm:
    kwargs = {"model": MODEL_ID, "temperature": 0.2, "max_tokens": 4000, "num_retries": 4}
    if api_key:
        kwargs["api_key"] = api_key
    return LiteLlm(**kwargs)


def build_workflow(api_key: str | None = None) -> Workflow:
    analyzer = Agent(
        name="analyzer",
        model=make_model(api_key),
        description="Analyzes the resume against the job description.",
        instruction=(
            "You are a recruiter and resume analyst. The user message contains a RESUME "
            "and a JOB DESCRIPTION. Produce an analysis with exactly these headings:\n"
            "1. CANDIDATE PROFILE: skills, experience, education, and projects, using only what is written.\n"
            "2. JOB REQUIREMENTS: the key skills and keywords the job asks for.\n"
            "3. MATCH SCORE: a number from 0 to 100 with a one-sentence reason.\n"
            "4. STRENGTHS: where the resume matches the job.\n"
            "5. GAPS: required skills or keywords missing from the resume.\n"
            "6. WEAKEST BULLETS: copy up to 5 weak or vague lines from the resume exactly as written.\n"
            "Be specific and honest. Never invent anything that is not in the resume."
        ),
    )

    rewriter = Agent(
        name="rewriter",
        model=make_model(api_key),
        description="Writes the final report with improved bullet points.",
        instruction=(
            "You are a professional resume coach. The input is an analysis of a candidate's "
            "resume against a job. Write the final report with these sections:\n"
            "1. SUMMARY: the match score written as 'Match score: NN/100' and a two-sentence overview.\n"
            "2. TOP 5 IMPROVEMENTS: the most important changes, in priority order.\n"
            "3. REWRITTEN BULLET POINTS: for each item under WEAKEST BULLETS, show BEFORE and AFTER, "
            "starting the AFTER with a strong action verb.\n"
            "4. KEYWORDS TO ADD: terms from the job requirements the candidate should include.\n"
            "5. SUGGESTED PROFESSIONAL SUMMARY: 3 lines tailored to this job.\n"
            "Rules: never invent experience, employers, or numbers. If a metric would help, "
            "write [add metric] as a placeholder for the candidate to fill in."
        ),
    )

    return Workflow(name="resume_reviewer", edges=[("START", analyzer, rewriter)])


# Used by `adk web`
root_agent = build_workflow()
