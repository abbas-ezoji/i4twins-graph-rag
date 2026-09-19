# Evidence Graph — V0

Minimal standalone RAG pipeline for the first implementation step.

## Pipeline

message → embedding → top-k retrieval → grounded prompt → Ollama generation → answer + sources

This version intentionally does not contain graph construction, claim extraction,
conflict detection, duplicate detection, reward scoring, or re-evaluation.

## Setup

Python 3.11+, Ollama, and a local model such as `gemma3:4b`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama pull gemma3:4b
```

Put the task corpus at `data/corpus.jsonl`.

Expected JSONL format:

```json
{"id":"DOC-01","title":"...","text":"..."}
```

The loader also accepts `document_id`, `doc_id`, `content`, and `body`.

## Run

```bash
uvicorn app.main:app --reload
```

Then use `/docs`, or:

```bash
curl -X POST http://localhost:8000/api/generation   -H "Content-Type: application/json"   -d '{"message":"What is the maximum pressure of P-200?","top_k":3}'
```

## Tests

```bash
pytest -q
```

The generation test uses a fake LLM and does not require Ollama.
