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

    # LLM
    llm_backend: str = os.getenv(
        "LLM_BACKEND",
        "ollama",
    )

    llm_model: str = os.getenv(
        "LLM_MODEL",
        "gemma3:4b",
    )

    ollama_host: str = os.getenv(
        "OLLAMA_HOST",
        "http://localhost:11434",
    )

    llm_timeout: int = int(
        os.getenv("LLM_TIMEOUT", "120")
    )

    # MongoDB
    mongodb_uri: str = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017",
    )

    mongodb_database: str = os.getenv(
        "MONGODB_DATABASE",
        "evidence_graph",
    )

    mongodb_collection: str = os.getenv(
        "MONGODB_COLLECTION",
        "structured_documents",
    )


settings = Settings()