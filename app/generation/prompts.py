SYSTEM_PROMPT = """You are a technical question-answering assistant.

Answer the user's question using only the provided retrieved documents.

Rules:
1. Do not invent technical facts.
2. If the documents do not contain enough information, say that the available
   documents do not provide enough information.
3. Keep the answer concise and factual.
4. Preserve important technical values and units exactly as supported by the documents.
5. When useful, mention the document IDs that support the answer.
"""


def build_generation_prompt(message: str, results: list) -> str:
    evidence_blocks = [
        f"[{item.document_id}] {item.title}\n{item.text}"
        for item in results
    ]
    evidence = "\n\n".join(evidence_blocks)

    return f"""User question:
{message}

Retrieved documents:
{evidence}

Answer the question using only the retrieved documents.
"""
