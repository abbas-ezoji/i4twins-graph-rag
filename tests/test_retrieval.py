import json

from app.retrieval.retriever import Retriever


class FakeEmbeddingClient:
    def embed(self, texts):
        vectors = []
        for text in texts:
            if "pump" in text.lower() or "pressure" in text.lower():
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors


def test_retrieval(tmp_path):
    corpus = tmp_path / "corpus.jsonl"
    records = [
        {
            "id": "DOC-01",
            "title": "Pump",
            "text": "P-200 maximum pressure is documented here.",
        },
        {
            "id": "DOC-02",
            "title": "Motor",
            "text": "M-50 motor maintenance information.",
        },
    ]
    corpus.write_text(
        "\n".join(json.dumps(x) for x in records),
        encoding="utf-8",
    )

    retriever = Retriever.from_jsonl(str(corpus), FakeEmbeddingClient())
    results = retriever.retrieve("What is the pump pressure?", top_k=1)

    assert len(results) == 1
    assert results[0].document_id == "DOC-01"
