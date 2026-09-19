from dataclasses import dataclass
import json
import sqlite3

import numpy as np


@dataclass
class IndexedDocument:
    document_id: str
    title: str
    text: str
    embedding: np.ndarray


class SQLiteEmbeddingStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL DEFAULT '',
                    text TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    embedding_model TEXT NOT NULL,
                    embedding_dimension INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def upsert(
        self,
        document_id: str,
        title: str,
        text: str,
        embedding: list[float],
        embedding_model: str,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (
                    document_id,
                    title,
                    text,
                    embedding,
                    embedding_model,
                    embedding_dimension
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    title = excluded.title,
                    text = excluded.text,
                    embedding = excluded.embedding,
                    embedding_model = excluded.embedding_model,
                    embedding_dimension = excluded.embedding_dimension
                """,
                (
                    document_id,
                    title,
                    text,
                    json.dumps(embedding),
                    embedding_model,
                    len(embedding),
                ),
            )
            conn.commit()

    def count(self) -> int:
        with self._connect() as conn:
            return int(
                conn.execute(
                    "SELECT COUNT(*) FROM documents"
                ).fetchone()[0]
            )

    def all_documents(self) -> list[IndexedDocument]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    document_id,
                    title,
                    text,
                    embedding
                FROM documents
                """
            ).fetchall()

        return [
            IndexedDocument(
                document_id=row["document_id"],
                title=row["title"],
                text=row["text"],
                embedding=np.asarray(
                    json.loads(row["embedding"]),
                    dtype=np.float32,
                ),
            )
            for row in rows
        ]

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[tuple[IndexedDocument, float]]:
        documents = self.all_documents()

        if not documents:
            return []

        query = np.asarray(
            query_embedding,
            dtype=np.float32,
        )

        matrix = np.vstack(
            [document.embedding for document in documents]
        )

        # Embeddings are normalized during creation,
        # therefore dot product is cosine similarity.
        scores = matrix @ query

        indices = np.argsort(scores)[::-1][:top_k]

        return [
            (
                documents[index],
                float(scores[index]),
            )
            for index in indices
        ]