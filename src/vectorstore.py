"""
FAISS Vector Store

Responsible for:
1. Creating embeddings
2. Building the FAISS vector database
3. Saving/loading the database
4. Similarity search
"""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import settings


# ==========================================================
# Embedding Model
# ==========================================================

def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Load the HuggingFace embedding model.
    """

    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


# ==========================================================
# Build Vector Store
# ==========================================================

def build_vectorstore(documents: List[Document]) -> FAISS:
    """
    Create a FAISS vector store from documents.
    """

    if not documents:
        raise ValueError("No documents provided.")

    embeddings = get_embeddings()

    return FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )


# ==========================================================
# Save Vector Store
# ==========================================================

def save_vectorstore(
    store: FAISS,
    path: str | None = None,
) -> None:
    """
    Save FAISS index to disk.
    """

    save_path = Path(path or settings.VECTORSTORE_DIR)

    save_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    store.save_local(str(save_path))


# ==========================================================
# Load Vector Store
# ==========================================================

def load_vectorstore(
    path: str | None = None,
) -> FAISS:
    """
    Load an existing FAISS index.
    """

    load_path = Path(path or settings.VECTORSTORE_DIR)

    if not load_path.exists():
        raise FileNotFoundError(
            "Vector store not found."
        )

    embeddings = get_embeddings()

    return FAISS.load_local(
        str(load_path),
        embeddings,
        allow_dangerous_deserialization=True,
    )


# ==========================================================
# Check Vector Store
# ==========================================================

def vectorstore_exists(
    path: str | None = None,
) -> bool:
    """
    Check whether the FAISS index exists.
    """

    check_path = Path(path or settings.VECTORSTORE_DIR)

    return (
        (check_path / "index.faiss").exists()
        and
        (check_path / "index.pkl").exists()
    )


# ==========================================================
# Similarity Search
# ==========================================================

def similarity_search(
    store: FAISS,
    query: str,
    k: int | None = None,
):
    """
    Retrieve the most relevant documents.
    """

    if not query.strip():
        raise ValueError("Query cannot be empty.")

    return store.similarity_search(
        query=query,
        k=k or settings.RETRIEVER_TOP_K,
    )