from app.embedding.local import LocalEmbeddingClient


def test_embedding_shape():
    client = LocalEmbeddingClient("sentence-transformers/all-MiniLM-L6-v2")
    vectors = client.embed(["industrial pump pressure"])

    assert len(vectors) == 1
    assert len(vectors[0]) > 0
