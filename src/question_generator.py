"""Generate tailored interview questions from the resume + job description."""
from src.rag_pipeline import get_llm, retrieve_context
from src.prompts import QUESTION_GENERATION_PROMPT


def generate_interview_questions(store, num_questions: int = 8) -> str:
    resume_context = retrieve_context(store, "candidate experience and skills", source_filter="resume", k=6)
    jd_context = retrieve_context(store, "role requirements and responsibilities", source_filter="job_description", k=6)

    prompt = QUESTION_GENERATION_PROMPT.format(
        jd_context=jd_context,
        resume_context=resume_context,
        num_questions=num_questions,
    )

    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content
