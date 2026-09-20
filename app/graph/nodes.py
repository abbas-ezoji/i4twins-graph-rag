import re

from app.graph.state import EvidenceGraphState
from app.embedding.local import LocalEmbeddingClient
from app.retrieval.index import SQLiteEmbeddingStore
from app.retrieval.retriever import Retriever
from app.utils.config import settings

from app.generation.prompts import (
    SYSTEM_PROMPT,
    build_evidence_prompt,
)
from app.llm.factory import get_llm_client


def retrieve_sub_queries(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    embedding_client = LocalEmbeddingClient(settings.embedding_model)
    index = SQLiteEmbeddingStore(settings.embedding_db_path)
    retriever = Retriever(
        embedding_client=embedding_client,
        index=index,
    )

    retrieved_documents = []

    for sub_query in state.get("sub_queries", []):
        results = retriever.retrieve(
            sub_query,
            top_k=3,
        )

        retrieved_documents.append(
            {
                "query": sub_query,
                "results": [
                    {
                        "document_id": result.document_id,
                        "title": result.title,
                        "text": result.text,
                        "score": result.score,
                    }
                    for result in results
                ],
            }
        )

    return {
        **state,
        "retrieved_documents": retrieved_documents,
        "current_node": "retrieve_sub_queries",
        "steps": state.get("steps", []) + ["retrieve_sub_queries"],
    }


def analyze_query(state: EvidenceGraphState) -> EvidenceGraphState:
    message = state["message"].strip()

    language = "fa" if re.search(r"[\u0600-\u06FF]", message) else "en"

    entities = []

    equipment_matches = re.findall(
        r"\b[A-Z]{1,5}-\d{1,5}\b",
        message,
    )

    for value in equipment_matches:
        entities.append(
            {
                "text": value,
                "type": "equipment",
                "normalized": value.upper(),
            }
        )

    attributes = []

    if any(
        term in message.lower()
        for term in [
            "pressure",
            "operating pressure",
            "فشار",
        ]
    ):
        attributes.append("operating_pressure")

    if any(
        term in message.lower()
        for term in [
            "maximum",
            "max",
            "حداکثر",
        ]
    ):
        attributes.append("maximum")

    intent = "retrieve_fact"

    return {
        **state,
        "language": language,
        "intent": intent,
        "entities": entities,
        "attributes": attributes,
        "current_node": "analyze_query",
        "steps": state.get("steps", []) + ["analyze_query"],
    }
    

def decompose_query(state: EvidenceGraphState) -> EvidenceGraphState:
    message = state["message"]

    entities = state.get("entities", [])
    attributes = state.get("attributes", [])

    sub_queries = []

    if entities and attributes:
        for entity in entities:
            entity_name = entity["normalized"]

            for attribute in attributes:
                if attribute == "operating_pressure":
                    sub_queries.append(
                        f"maximum operating pressure of {entity_name}"
                    )
    else:
        sub_queries.append(message)

    return {
        **state,
        "sub_queries": sub_queries,
        "current_node": "decompose_query",
        "steps": state.get("steps", []) + ["decompose_query"],
    }
    

def aggregate_evidence(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    evidence_by_document = {}

    for group in state.get("retrieved_documents", []):
        query = group["query"]

        for result in group["results"]:
            document_id = result["document_id"]

            if document_id not in evidence_by_document:
                evidence_by_document[document_id] = {
                    "document_id": document_id,
                    "title": result["title"],
                    "text": result["text"],
                    "score": result["score"],
                    "matched_queries": [query],
                }
            else:
                existing = evidence_by_document[document_id]

                existing["score"] = max(
                    existing["score"],
                    result["score"],
                )

                if query not in existing["matched_queries"]:
                    existing["matched_queries"].append(query)

    evidence = sorted(
        evidence_by_document.values(),
        key=lambda item: item["score"],
        reverse=True,
    )

    return {
        **state,
        "evidence": evidence,
        "current_node": "aggregate_evidence",
        "steps": state.get("steps", []) + ["aggregate_evidence"],
    }
    
def detect_evidence_status(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    evidence = state.get("evidence", [])

    if not evidence:
        return {
            **state,
            "answer_status": "INSUFFICIENT",
            "metadata": {
                **state.get("metadata", {}),
                "evidence_status_reason": "No evidence retrieved.",
            },
            "current_node": "detect_evidence_status",
            "steps": state.get("steps", []) + ["detect_evidence_status"],
        }

    pressure_values = []

    for item in evidence:
        text = item.get("text", "")

        matches = re.findall(
            r"(?i)(?:maximum operating pressure|rated pressure|pressure)"
            r".{0,80}?"
            r"(\d+(?:\.\d+)?)\s*(bar|psi|kPa|MPa)",
            text,
        )

        for value, unit in matches:
            pressure_values.append(
                {
                    "value": float(value),
                    "unit": unit.lower(),
                    "document_id": item["document_id"],
                }
            )

    distinct_values = {
        (item["value"], item["unit"])
        for item in pressure_values
    }

    if len(distinct_values) > 1:
        status = "CONFLICTING"
        reason = "Multiple evidence values were found for the same pressure-related fact."
    else:
        status = "SUFFICIENT"
        reason = "Evidence contains a consistent factual value."

    return {
        **state,
        "answer_status": status,
        "metadata": {
            **state.get("metadata", {}),
            "evidence_status_reason": reason,
            "extracted_values": pressure_values,
        },
        "current_node": "detect_evidence_status",
        "steps": state.get("steps", []) + ["detect_evidence_status"],
    }


def filter_relevant_evidence(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    evidence = state.get("evidence", [])
    entities = state.get("entities", [])

    normalized_entities = {
        entity.get("normalized", "").upper()
        for entity in entities
        if entity.get("normalized")
    }

    # If query has no explicit entities, keep the retrieved evidence.
    if not normalized_entities:
        relevant_evidence = evidence
    else:
        relevant_evidence = []

        for item in evidence:
            document_text = (
                f"{item.get('title', '')}\n"
                f"{item.get('text', '')}"
            ).upper()

            if any(
                entity in document_text
                for entity in normalized_entities
            ):
                relevant_evidence.append(item)

    return {
        **state,
        "evidence": relevant_evidence,
        "current_node": "filter_relevant_evidence",
        "steps": state.get("steps", [])
        + ["filter_relevant_evidence"],
    }


def generate_conflict_answer(
    state: EvidenceGraphState,
) -> EvidenceGraphState:

    llm = get_llm_client()

    prompt = build_evidence_prompt(
        question=state["message"],
        evidence=state.get("evidence", []),
        status=state.get("answer_status", "CONFLICTING"),
    )

    answer = llm.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    return {
        **state,
        "answer": answer,
        "current_node": "generate_conflict_answer",
        "steps": state.get("steps", [])
        + ["generate_conflict_answer"],
    }


def generate_answer(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    llm = get_llm_client()

    prompt = build_evidence_prompt(
        question=state["message"],
        evidence=state.get("evidence", []),
        status=state.get("answer_status", "SUFFICIENT"),
    )

    answer = llm.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    return {
        **state,
        "answer": answer,
        "current_node": "generate_answer",
        "steps": state.get("steps", [])
        + ["generate_answer"],
    }


def generate_conflict_answer(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    llm = get_llm_client()

    prompt = build_evidence_prompt(
        question=state["message"],
        evidence=state.get("evidence", []),
        status=state.get("answer_status", "CONFLICTING"),
    )

    answer = llm.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    return {
        **state,
        "answer": answer,
        "current_node": "generate_conflict_answer",
        "steps": state.get("steps", [])
        + ["generate_conflict_answer"],
    }


def clarification(
    state: EvidenceGraphState,
) -> EvidenceGraphState:
    llm = get_llm_client()

    question = state["message"]
    evidence = state.get("evidence", [])
    language = state.get("language", "en")

    if language == "fa":
        language_instruction = "پاسخ را به زبان فارسی بده."
    else:
        language_instruction = "Answer in English."

    evidence_text = "\n\n".join(
        [
            f"Document: {item['document_id']}\n"
            f"Title: {item['title']}\n"
            f"Content:\n{item['text']}"
            for item in evidence
        ]
    )

    prompt = f"""
User question:
{question}

Evidence status:
INSUFFICIENT

Available evidence:
{evidence_text if evidence_text else "No relevant evidence was found."}

The available evidence is insufficient to answer the user's question reliably.

Your task is to ask the user for the minimum clarification needed
to continue the retrieval process.

Rules:
1. Do not answer the original question.
2. Do not invent facts.
3. Do not assume missing information.
4. Ask one concise and useful clarification question.
5. If the entity is unknown, ask the user to identify or provide the correct entity.
6. If the requested attribute is unclear, ask which attribute they mean.
7. Keep the clarification directly related to the original question.
8. {language_instruction}

Return only the clarification question.
"""

    answer = llm.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    return {
        **state,
        "answer": answer,
        "current_node": "clarification",
        "steps": state.get("steps", [])
        + ["clarification"],
    }