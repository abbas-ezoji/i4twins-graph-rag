from app.llm.client import LLMClient
from app.llm.ollama import OllamaClient
from app.utils.config import settings


def get_llm_client() -> LLMClient:
    backend = settings.llm_backend.lower()

    if backend == "ollama":
        return OllamaClient(
            host=settings.ollama_host,
            model=settings.llm_model,
            timeout=settings.llm_timeout,
        )

    raise ValueError(
        f"Unsupported LLM backend: {settings.llm_backend}"
    )