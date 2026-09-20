from typing import Any, TypedDict


class EvidenceGraphState(TypedDict, total=False):
    session_id: str

    # Original request
    message: str
    language: str

    # Query understanding
    intent: str
    entities: list[dict[str, Any]]
    attributes: list[str]
    sub_queries: list[str]

    # Retrieval
    retrieved_documents: list[dict[str, Any]]

    # Final stages
    evidence: list[dict[str, Any]]
    answer: str
    answer_status: str

    # Execution metadata
    current_node: str
    steps: list[str]
    error: str | None
    metadata: dict[str, Any]