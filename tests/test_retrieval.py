from app.embedding.local import LocalEmbeddingClient
from app.retrieval.index import SQLiteEmbeddingStore
from app.retrieval.retriever import Retriever
from app.utils.config import settings


def main() -> None:
    embedding_client = LocalEmbeddingClient(
        settings.embedding_model
    )

    store = SQLiteEmbeddingStore(
        settings.embedding_db_path
    )

    retriever = Retriever(
        embedding_client=embedding_client,
        index=store,
    )

    query = "What is the operating pressure of P-200?"

    results = retriever.retrieve(
        query=query,
        top_k=5,
    )

    print(f"\nQuery: {query}\n")

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. "
            f"{result.document_id} | "
            f"{result.score:.4f} | "
            f"{result.title}"
        )


if __name__ == "__main__":
    main()