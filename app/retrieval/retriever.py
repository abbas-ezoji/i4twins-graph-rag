from dataclasses import dataclass

from app.embedding.client import EmbeddingClient
from app.retrieval.index import SQLiteEmbeddingStore


@dataclass
class RetrievalResult:
    document_id: str
    title: str
    text: str
    score: float


class Retriever:
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        index: SQLiteEmbeddingStore,
    ):
        self.embedding_client = embedding_client
        self.index = index

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[RetrievalResult]:
        if not query or not query.strip():
            return []

        query_embedding = self.embedding_client.embed(
            [query.strip()]
        )[0]

        hits = self.index.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        return [
            RetrievalResult(
                document_id=document.document_id,
                title=document.title,
                text=document.text,
                score=score,
            )
            for document, score in hits
        ]