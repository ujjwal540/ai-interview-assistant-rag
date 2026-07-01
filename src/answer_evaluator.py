"""Score / give feedback on a candidate's practice answer using retrieved resume context."""
from src.rag_pipeline import get_llm, retrieve_context
from src.prompts import ANSWER_EVALUATION_PROMPT


def evaluate_answer(store, question: str, answer: str) -> str:
    resume_context = retrieve_context(store, question, source_filter="resume", k=5)

    prompt = ANSWER_EVALUATION_PROMPT.format(
        question=question,
        answer=answer,
        resume_context=resume_context,
    )

    llm = get_llm()
    response = llm.invoke(prompt)
    return response.content
