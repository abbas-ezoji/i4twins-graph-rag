from app.graph.workflow import build_graph


def main():
    graph = build_graph()

    result = graph.invoke(
        {
            "session_id": "test-sufficient-001",
            "message": "What is the replacement interval for bearing BRG-4410?",
            "steps": [],
        }
    )

    print("\n=== SUFFICIENT Graph Result ===")

    print("Language:", result.get("language"))
    print("Intent:", result.get("intent"))
    print("Entities:", result.get("entities"))
    print("Attributes:", result.get("attributes"))
    print("Sub Queries:", result.get("sub_queries"))

    print("\nRetrieved Documents:")
    for group in result.get("retrieved_documents", []):
        print(f"\nQuery: {group['query']}")
        for item in group["results"]:
            print(
                f"  {item['document_id']} | "
                f"{item['score']:.4f} | "
                f"{item['title']}"
            )

    print("\nSteps:")
    print(result.get("steps"))

    print("\nEvidence:")
    for item in result.get("evidence", []):
        print(
            f"  {item['document_id']} | "
            f"{item['score']:.4f} | "
            f"{item['title']}"
        )

    print("\nEvidence Status:")
    print("Status:", result.get("answer_status"))
    print(
        "Reason:",
        result.get("metadata", {}).get("evidence_status_reason"),
    )
    print(
        "Extracted Values:",
        result.get("metadata", {}).get("extracted_values"),
    )

    print("\nAnswer:")
    print(result.get("answer"))


if __name__ == "__main__":
    main()