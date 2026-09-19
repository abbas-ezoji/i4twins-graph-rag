import json
from pathlib import Path

from app.embedding.local import LocalEmbeddingClient
from app.retrieval.index import SQLiteEmbeddingStore
from app.utils.config import settings


def main() -> None:
    corpus_path = Path(settings.corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus not found: {corpus_path}"
        )

    embedding_client = LocalEmbeddingClient(
        settings.embedding_model
    )

    store = SQLiteEmbeddingStore(
        settings.embedding_db_path
    )

    documents = []

    with corpus_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON at {corpus_path}:{line_number}"
                ) from exc

            document_id = str(
                record.get("id")
                or record.get("document_id")
                or record.get("doc_id")
                or f"DOC-{line_number:03d}"
            )

            title = str(
                record.get("title")
                or record.get("name")
                or ""
            )

            text = str(
                record.get("text")
                or record.get("content")
                or record.get("body")
                or ""
            ).strip()

            if text:
                documents.append(
                    (document_id, title, text)
                )

    if not documents:
        raise ValueError("No valid documents found in corpus.")

    texts = [
        f"{title}\n{text}".strip()
        for _, title, text in documents
    ]

    embeddings = embedding_client.embed(texts)

    if len(embeddings) != len(documents):
        raise RuntimeError(
            "Embedding count does not match document count."
        )

    for (document_id, title, text), embedding in zip(
        documents,
        embeddings,
    ):
        store.upsert(
            document_id=document_id,
            title=title,
            text=text,
            embedding=embedding,
            embedding_model=settings.embedding_model,
        )

    print(
        f"Indexed {store.count()} documents "
        f"into {settings.embedding_db_path}"
    )


if __name__ == "__main__":
    main()