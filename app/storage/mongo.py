from typing import Any

from pymongo import MongoClient

from app.structure.models import StructuredDocument


class MongoStructuredStore:
    def __init__(
        self,
        uri: str,
        database: str,
        collection: str = "structured_documents",
    ):
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self.collection = self.db[collection]

        self.collection.create_index(
            "document_id",
            unique=True,
        )

    def upsert(
        self,
        document: StructuredDocument,
    ) -> None:
        payload = document.model_dump()

        self.collection.replace_one(
            {"document_id": document.document_id},
            payload,
            upsert=True,
        )

    def get(
        self,
        document_id: str,
    ) -> dict[str, Any] | None:
        return self.collection.find_one(
            {"document_id": document_id}
        )

    def get_many(
        self,
        document_ids: list[str],
    ) -> list[dict[str, Any]]:
        if not document_ids:
            return []

        return list(
            self.collection.find(
                {
                    "document_id": {
                        "$in": document_ids
                    }
                }
            )
        )

    def count(self) -> int:
        return self.collection.count_documents({})

    def delete(
        self,
        document_id: str,
    ) -> None:
        self.collection.delete_one(
            {"document_id": document_id}
        )

    def close(self) -> None:
        self.client.close()