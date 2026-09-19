from functools import lru_cache

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.embedding.local import LocalEmbeddingClient
from app.generation.generator import Generator
from app.llm.ollama import OllamaClient
from app.retrieval.retriever import Retriever
from app.utils.config import settings

router = APIRouter(tags=["generation"])


class GenerationRequest(BaseModel):
    message: str = Field(min_length=1)
    top_k: int = Field(default=settings.top_k, ge=1, le=20)


class Source(BaseModel):
    document_id: str
    title: str = ""
    score: float
    text: str


class GenerationResponse(BaseModel):
    answer: str
    sources: list[Source]


@lru_cache
def get_retriever() -> Retriever:
    return Retriever.from_jsonl(
        path=settings.corpus_path,
        embedding_client=LocalEmbeddingClient(settings.embedding_model),
    )


@lru_cache
def get_generator() -> Generator:
    return Generator(
        llm_client=OllamaClient(
            host=settings.ollama_host,
            model=settings.llm_model,
        )
    )


@router.post("/generation", response_model=GenerationResponse)
def generate(request: GenerationRequest) -> GenerationResponse:
    try:
        results = get_retriever().retrieve(request.message, top_k=request.top_k)
        answer = get_generator().generate(request.message, results)
        return GenerationResponse(
            answer=answer,
            sources=[
                Source(
                    document_id=x.document_id,
                    title=x.title,
                    score=x.score,
                    text=x.text,
                )
                for x in results
            ],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
