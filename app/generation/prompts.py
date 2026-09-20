SYSTEM_PROMPT = """
You are an evidence-grounded assistant.

Answer the user's question only using the provided evidence.

Rules:
1. Do not invent facts.
2. Do not use information outside the evidence.
3. If evidence contains conflicting values, explicitly report the conflict.
4. Mention the relevant document IDs when presenting factual claims.
5. If the evidence is insufficient, say that the available evidence is insufficient.
6. Answer in the user's language.
"""


def build_evidence_prompt(
    question: str,
    evidence: list[dict],
    status: str,
) -> str:
    evidence_text = "\n\n".join(
        [
            (
                f"Document: {item['document_id']}\n"
                f"Title: {item['title']}\n"
                f"Score: {item['score']:.4f}\n"
                f"Content:\n{item['text']}"
            )
            for item in evidence
        ]
    )

    return f"""
    User question:
    {question}

    Evidence status:
    {status}

    Evidence:
    {evidence_text}

    Generate a grounded answer to the user question.
    """

def build_generation_prompt(
    question: str,
    evidence: list[dict],
    status: str = "SUFFICIENT",
) -> str:
    evidence_text = "\n\n".join(
        [
            f"Document: {item['document_id']}\n"
            f"Title: {item['title']}\n"
            f"Score: {item.get('score', 0.0):.4f}\n"
            f"Content:\n{item['text']}"
            for item in evidence
        ]
    )

    return f"""
User question:
{question}

Evidence status:
{status}

Evidence:
{evidence_text if evidence_text else "No relevant evidence was found."}

Generate a grounded answer to the user question.
"""