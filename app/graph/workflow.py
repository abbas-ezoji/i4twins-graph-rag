from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    analyze_query,
    decompose_query,
    retrieve_sub_queries,
    aggregate_evidence,
    filter_relevant_evidence,
    detect_evidence_status,
    generate_answer,
    generate_conflict_answer,
    clarification,
)
from app.graph.state import EvidenceGraphState


def route_after_evidence_status(
    state: EvidenceGraphState,
) -> str:
    status = state.get("answer_status")

    if status == "CONFLICTING":
        return "generate_conflict_answer"

    if status == "INSUFFICIENT":
        return "clarification"

    return "generate_answer"


def build_graph():
    graph = StateGraph(EvidenceGraphState)

    graph.add_node("analyze_query", analyze_query)
    graph.add_node("decompose_query", decompose_query)
    graph.add_node("retrieve_sub_queries", retrieve_sub_queries)
    graph.add_node("aggregate_evidence", aggregate_evidence)
    graph.add_node(
        "filter_relevant_evidence",
        filter_relevant_evidence,
    )
    graph.add_node("detect_evidence_status", detect_evidence_status)

    graph.add_node("generate_answer", generate_answer)
    graph.add_node(
        "generate_conflict_answer",
        generate_conflict_answer,
    )
    graph.add_node("clarification", clarification)

    graph.add_edge(START, "analyze_query")
    graph.add_edge("analyze_query", "decompose_query")
    graph.add_edge("decompose_query", "retrieve_sub_queries")
    graph.add_edge("retrieve_sub_queries", "aggregate_evidence")

    graph.add_edge(
        "aggregate_evidence",
        "filter_relevant_evidence",
    )

    graph.add_edge(
        "filter_relevant_evidence",
        "detect_evidence_status",
    )

    graph.add_conditional_edges(
        "detect_evidence_status",
        route_after_evidence_status,
        {
            "generate_answer": "generate_answer",
            "generate_conflict_answer": "generate_conflict_answer",
            "clarification": "clarification",
        },
    )

    graph.add_edge("generate_answer", END)
    graph.add_edge("generate_conflict_answer", END)
    graph.add_edge("clarification", END)

    return graph.compile()