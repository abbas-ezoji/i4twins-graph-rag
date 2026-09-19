import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    ollama_host: str = os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434",
    )

    llm_model: str = os.getenv(
        "LLM_MODEL",
        "gemma3:4b",
    )

    top_k: int = int(
        os.getenv("TOP_K", "3")
    )

    corpus_path: str = os.getenv(
        "CORPUS_PATH",
        "data/corpus.jsonl",
    )

    embedding_db_path: str = os.getenv(
        "EMBEDDING_DB_PATH",
        "data/embeddings.db",
    )


settings = Settings()