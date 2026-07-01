from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm():
    settings.validate()

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
    )

    return llm


def get_retriever(store, k: int = None):
    k = k or settings.RETRIEVER_TOP_K
    return store.as_retriever(search_kwargs={"k": k})


def retrieve_context(store, query: str, source_filter: str = None, k: int = None) -> str:
    retriever = get_retriever(store, k=k)
    docs = retriever.invoke(query)

    if source_filter:
        docs = [d for d in docs if d.metadata.get("source") == source_filter] or docs

    return "\n---\n".join(d.page_content for d in docs)