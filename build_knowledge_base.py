import json
from pathlib import Path

from app.embedding.local import LocalEmbeddingClient
from app.retrieval.index import SQLiteEmbeddingStore
from app.storage.mongo import MongoStructuredStore
from app.structure.basic import BasicStructureExtractor
from app.utils.config import settings


def load_documents(corpus_path: Path) -> list[tuple[str, str, str]]:
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

    return documents


def main() -> None:
    corpus_path = Path(settings.corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus not found: {corpus_path}"
        )

    documents = load_documents(corpus_path)

    if not documents:
        raise ValueError(
            "No valid documents found in corpus."
        )

    # --------------------------------------------------
    # Semantic pipeline
    # --------------------------------------------------

    embedding_client = LocalEmbeddingClient(
        settings.embedding_model
    )

    semantic_store = SQLiteEmbeddingStore(
        settings.embedding_db_path
    )

    texts = [
        f"{title}\n{text}".strip()
        for _, title, text in documents
    ]

    embeddings = embedding_client.embed(texts)

    if len(embeddings) != len(documents):
        raise RuntimeError(
            "Embedding count does not match document count."
        )

    # --------------------------------------------------
    # Structure pipeline
    # --------------------------------------------------

    extractor = BasicStructureExtractor()

    mongo_store = MongoStructuredStore(
        uri=settings.mongodb_uri,
        database=settings.mongodb_database,
        collection=settings.mongodb_collection,
    )

    # --------------------------------------------------
    # Process documents
    # --------------------------------------------------

    for (
        (document_id, title, text),
        embedding,
    ) in zip(documents, embeddings):

        # 1. Store semantic representation
        semantic_store.upsert(
            document_id=document_id,
            title=title,
            text=text,
            embedding=embedding,
            embedding_model=settings.embedding_model,
        )

        # 2. Extract structured representation
        structured_document = extractor.extract(
            document_id=document_id,
            title=title,
            text=text,
        )

        # 3. Store structured representation
        mongo_store.upsert(
            structured_document
        )

    print()
    print("Knowledge base build completed.")
    print(
        f"Documents: {len(documents)}"
    )
    print(
        f"Semantic index: "
        f"{settings.embedding_db_path}"
    )
    print(
        f"Semantic documents: "
        f"{semantic_store.count()}"
    )
    print(
        f"MongoDB database: "
        f"{settings.mongodb_database}"
    )
    print(
        f"MongoDB collection: "
        f"{settings.mongodb_collection}"
    )
    print(
        f"Structured documents: "
        f"{mongo_store.count()}"
    )

    mongo_store.close()


if __name__ == "__main__":
    main()