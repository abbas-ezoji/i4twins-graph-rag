from dataclasses import dataclass
import numpy as np


@dataclass
class IndexedDocument:
    document_id: str
    title: str
    text: str
    embedding: np.ndarray


class InMemoryIndex:
    def __init__(self, documents: list[IndexedDocument]):
        self.documents = documents

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[tuple[IndexedDocument, float]]:
        if not self.documents:
            return []

        query = np.asarray(query_embedding, dtype=np.float32)
        matrix = np.vstack([doc.embedding for doc in self.documents])
        scores = matrix @ query
        indices = np.argsort(scores)[::-1][:top_k]

        return [(self.documents[i], float(scores[i])) for i in indices]
