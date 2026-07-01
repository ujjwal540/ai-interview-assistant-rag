import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    VECTORSTORE_DIR: str = os.getenv("VECTORSTORE_DIR", "vectorstore")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", 4))

    def validate(self):
        if not self.GEMINI_API_KEY:
            raise ValueError("Missing GEMINI_API_KEY")


settings = Settings()