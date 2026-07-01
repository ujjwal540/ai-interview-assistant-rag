"""A stateful mock-interview chat: Claude asks questions, reacts to answers, keeps history."""
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.rag_pipeline import get_llm, retrieve_context
from src.prompts import MOCK_INTERVIEW_SYSTEM_PROMPT


class MockInterviewSession:
    def __init__(self, store):
        self.store = store
        self.llm = get_llm()
        resume_context = retrieve_context(store, "candidate background", source_filter="resume", k=6)
        jd_context = retrieve_context(store, "role requirements", source_filter="job_description", k=6)
        system_prompt = MOCK_INTERVIEW_SYSTEM_PROMPT.format(
            resume_context=resume_context, jd_context=jd_context
        )
        self.history = [SystemMessage(content=system_prompt)]

    def start(self) -> str:
        self.history.append(HumanMessage(content="Please begin the interview with your first question."))
        return self._call()

    def respond(self, candidate_answer: str) -> str:
        self.history.append(HumanMessage(content=candidate_answer))
        return self._call()

    def _call(self) -> str:
        response = self.llm.invoke(self.history)
        self.history.append(AIMessage(content=response.content))
        return response.content
