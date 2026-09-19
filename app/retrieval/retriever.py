import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.embedding.client import EmbeddingClient
from app.retrieval.index import IndexedDocument, InMemoryIndex


@dataclass
class RetrievalResult:
    document_id: str
    title: str
    text: str
    score: float


class Retriever:
    def __init__(self, embedding_client: EmbeddingClient, index: InMemoryIndex):
        self.embedding_client = embedding_client
        self.index = index

    @classmethod
    def from_jsonl(cls, path: str, embedding_client: EmbeddingClient) -> "Retriever":
        corpus_path = Path(path)
        if not corpus_path.exists():
            raise FileNotFoundError(f"Corpus not found: {corpus_path}")

        records = []
        with corpus_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON at {corpus_path}:{line_number}"
                    ) from exc

        normalized = []
        for i, record in enumerate(records):
            document_id = str(
                record.get("id")
                or record.get("document_id")
                or record.get("doc_id")
                or f"DOC-{i + 1:03d}"
            )
            title = str(record.get("title") or record.get("name") or "")
            text = str(
                record.get("text")
                or record.get("content")
                or record.get("body")
                or ""
            ).strip()

            if text:
                normalized.append((document_id, title, text))

        texts = [f"{title}
{text}".strip() for _, title, text in normalized]
        embeddings = embedding_client.embed(texts)

        documents = [
            IndexedDocument(
                document_id=document_id,
                title=title,
                text=text,
                embedding=np.asarray(embedding, dtype=np.float32),
            )
            for (document_id, title, text), embedding
            in zip(normalized, embeddings)
        ]

        return cls(
            embedding_client=embedding_client,
            index=InMemoryIndex(documents),
        )

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_embedding = self.embedding_client.embed([query])[0]
        hits = self.index.search(query_embedding, top_k=top_k)

        return [
            RetrievalResult(
                document_id=document.document_id,
                title=document.title,
                text=document.text,
                score=score,
            )
            for document, score in hits
        ]
