from typing import Any, TypedDict


class EvidenceGraphState(TypedDict, total=False):

    # =========================
    # Context
    # =========================

    session_id: str
    user_id: str
    language: str

    # =========================
    # Input
    # =========================

    message: str

    # =========================
    # Query Analysis
    # =========================

    claims: list[dict[str, Any]]

    # =========================
    # Retrieval
    # =========================

    query_embeddings: list[list[float]]

    retrieved_documents: list[dict[str, Any]]

    # =========================
    # Evidence Processing
    # =========================

    clusters: list[dict[str, Any]]

    evidence: list[dict[str, Any]]

    # =========================
    # Generation
    # =========================

    answer: str
    answer_status: str

    # =========================
    # Runtime
    # =========================

    current_node: str
    steps: list[str]

    # =========================
    # Errors / metadata
    # =========================

    error: str | None
    metadata: dict[str, Any]