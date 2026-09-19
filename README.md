# Evidence Graph — V0

Minimal Evidence Graph prototype with persistent embeddings, baseline retrieval, and a grounded generation layer.

## Current Pipeline

The current implementation is being built incrementally:

```text
corpus.jsonl
    ↓
embedding
    ↓
SQLite embedding store
    ↓
query
    ↓
query embedding
    ↓
Top-K retrieval
```

The next stage will add query decomposition so that a single user query can be converted into multiple tasks/sub-queries and processed through the Evidence Graph.

The project currently does **not** yet contain query decomposition, graph construction, claim extraction, conflict detection, duplicate detection, reward scoring, or re-evaluation.

## Architecture

### Embedding / Indexing

Documents are loaded from `data/corpus.jsonl`, embedded with the configured local embedding model, and persisted in SQLite.

```text
data/corpus.jsonl
        ↓
LocalEmbeddingClient
        ↓
SQLiteEmbeddingStore
        ↓
data/embeddings.db
```

Embeddings are persisted so retrieval does not need to re-embed the entire corpus on every run.

### Retrieval

The retrieval path is intentionally simple at this stage:

```text
User Query
    ↓
EmbeddingClient
    ↓
SQLiteEmbeddingStore.search()
    ↓
Top-K documents
```

Retrieval uses vector similarity over the stored embeddings.

## Setup

Python 3.10+, Ollama, and a local model such as `gemma3:4b`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull gemma3:4b
```

Put the task corpus at:

```text
data/corpus.jsonl
```

Expected JSONL format:

```json
{"id":"DOC-01","title":"...","text":"..."}
```

The loader also accepts `document_id`, `doc_id`, `content`, and `body`.

## Build Embeddings

Before testing retrieval, build the persistent embedding store:

```bash
python build_embeddings.py
```

Expected output:

```text
Indexed <N> documents into data/embeddings.db
```

This step creates or updates:

```text
data/embeddings.db
```

## Test Retrieval

After building the embedding database, run the baseline retrieval test:

```bash
python test_retrieval_manual.py
```

The test performs:

```text
query
  ↓
query embedding
  ↓
SQLite search
  ↓
Top-K results
```

At this stage, the purpose is only to validate the embedding and retrieval layers before introducing query decomposition and LangGraph orchestration.

## API

The API remains available for the project:

```bash
uvicorn app.main:app --reload
```

Then use `/docs`.

Example:

```bash
curl -X POST http://localhost:8000/api/generation \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the maximum pressure of P-200?","top_k":3}'
```

The API/generation path will be aligned with the new persistent retrieval layer as the implementation progresses.

## Tests

```bash
pytest -q
```

The existing generation test uses a fake LLM and does not require Ollama.

## Roadmap

The implementation is intentionally incremental:

1. **Embedding persistence** — completed/in progress
2. **Baseline retrieval** — current step
3. **Retrieval validation with real queries**
4. **Query decomposition into multiple tasks/sub-queries**
5. **LangGraph orchestration**
6. **Evidence aggregation and generation**
7. **Evaluation, conflict handling, and re-evaluatio**
