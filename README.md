# Evidence Graph â€” V0

Lightweight, persistent, evidence-grounded RAG prototype built incrementally around LangGraph orchestration.

## Current Status

The current implementation includes:

- Persistent local embeddings
- SQLite vector retrieval
- Query analysis and decomposition
- LangGraph workflow orchestration
- Evidence aggregation
- Entity-based evidence filtering
- Evidence status detection
- Grounded answer generation
- Conflict-aware answer generation
- Insufficient-evidence clarification
- Provider-agnostic LLM interface with Ollama backend

The implementation is intentionally incremental. Structured knowledge extraction, MongoDB-backed facts/relations, hybrid retrieval, and advanced evidence reasoning are planned next.

## Current Pipeline

```text
User Query
    â†“
analyze_query
    â†“
decompose_query
    â†“
retrieve_sub_queries
    â†“
aggregate_evidence
    â†“
filter_relevant_evidence
    â†“
detect_evidence_status
    â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  SUFFICIENT   â”‚   CONFLICTING    â”‚   INSUFFICIENT   â”‚
â†“               â†“                  â†“
generate_answer generate_conflict  clarification
                _answer
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                        â†“
                       END
```

## Architecture

### Embedding / Indexing

```text
data/corpus.jsonl
        â†“
LocalEmbeddingClient
        â†“
SQLiteEmbeddingStore
        â†“
data/embeddings.db
```

Embeddings are persisted so retrieval does not need to re-embed the corpus for every query.

### Retrieval

```text
User Query
    â†“
EmbeddingClient
    â†“
SQLiteEmbeddingStore.search()
    â†“
Top-K documents
```

Retrieval currently uses vector similarity over stored embeddings.

### Query Analysis and Decomposition

The graph analyzes language, intent, explicit entities, and query attributes, then converts the query into one or more retrieval sub-queries.

Example:

```text
Ø­Ø¯Ø§Ú©Ø«Ø± ÙØ´Ø§Ø± Ú©Ø§Ø±ÛŒ Ù¾Ù…Ù¾ P-200 Ú†Ù‚Ø¯Ø± Ø§Ø³ØªØŸ
        â†“
maximum operating pressure of P-200
```

### Evidence Aggregation and Filtering

Retrieved results are deduplicated by document ID and aggregated into a unified evidence list. Evidence is then filtered against explicit query entities so unrelated documents do not participate in evidence evaluation.

Example:

```text
Retrieved:
DOC-01 â†’ P-200
DOC-02 â†’ P-200
DOC-03 â†’ C-100

After filtering:
DOC-01 â†’ P-200
DOC-02 â†’ P-200
```

## Evidence Status and Routing

The workflow currently supports three outcomes:

### SUFFICIENT

Relevant evidence is available and supports an answer.

```text
detect_evidence_status
        â†“
    SUFFICIENT
        â†“
 generate_answer
```

### CONFLICTING

Multiple conflicting values are detected for the same currently supported pressure-related fact. The system reports the conflicting sources instead of silently selecting one.

```text
detect_evidence_status
        â†“
    CONFLICTING
        â†“
generate_conflict_answer
```

### INSUFFICIENT

No relevant evidence remains after filtering. The system asks the user for the minimum clarification needed to continue.

```text
detect_evidence_status
        â†“
    INSUFFICIENT
        â†“
    clarification
```

## LLM Layer

The LLM layer is provider-agnostic through `LLMClient` and a backend factory.

Current backend:

```text
Ollama â†’ gemma3:4b
```

Configuration:

```env
LLM_BACKEND=ollama
LLM_MODEL=gemma3:4b
OLLAMA_HOST=http://localhost:11434
LLM_TIMEOUT=120
```

Additional providers can be added without changing graph nodes.

## Generation

Generation is evidence-grounded. The system instructs the model to:

- answer only from supplied evidence
- avoid inventing facts
- mention relevant document IDs
- explicitly report conflicts
- state when evidence is insufficient
- answer in the user's language

The three response paths are implemented separately:

```text
SUFFICIENT    â†’ grounded answer
CONFLICTING   â†’ conflict-aware grounded answer
INSUFFICIENT  â†’ clarification question
```

## Setup

Requirements:

- Python 3.10+
- Ollama
- A local model such as `gemma3:4b`

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

```bash
python build_embeddings.py
```

This creates or updates:

```text
data/embeddings.db
```

## Test Retrieval

```bash
python test_retrieval_manual.py
```

## Test the LangGraph Workflow

Three graph-level tests cover the three routing outcomes.

### Sufficient Evidence

```bash
python -m tests.test_graph_sufficient
```

Example query:

```text
What is the replacement interval for bearing BRG-4410?
```

Expected route:

```text
... â†’ detect_evidence_status
        â†“
    SUFFICIENT
        â†“
 generate_answer
```

### Conflicting Evidence

```bash
python -m tests.test_graph_conflict
```

Example query:

```text
Ø­Ø¯Ø§Ú©Ø«Ø± ÙØ´Ø§Ø± Ú©Ø§Ø±ÛŒ Ù¾Ù…Ù¾ P-200 Ú†Ù‚Ø¯Ø± Ø§Ø³ØªØŸ
```

Expected route:

```text
... â†’ detect_evidence_status
        â†“
    CONFLICTING
        â†“
generate_conflict_answer
```

The current corpus contains two different maximum-pressure values for P-200, so both source documents are reported.

### Insufficient Evidence / Clarification

```bash
python -m tests.test_graph_clarification
```

Example query:

```text
Ø¯Ù…Ø§ÛŒ Ú©Ø§Ø±ÛŒ ØªØ¬Ù‡ÛŒØ² ZX-999 Ú†Ù‚Ø¯Ø± Ø§Ø³ØªØŸ
```

Expected route:

```text
... â†’ filter_relevant_evidence
        â†“
      no evidence
        â†“
    INSUFFICIENT
        â†“
    clarification
```

## API

The API remains available:

```bash
python -m uvicorn app.main:app --reload
```

Then open `/docs`.

Example:

```bash
curl -X POST http://localhost:8000/api/generation \
  -H "Content-Type: application/json" \
  -d '{"message":"What is the maximum pressure of P-200?","top_k":3}'
```

The API layer will be aligned further with the LangGraph workflow as orchestration is integrated into the serving path.

## Tests

Run the existing suite:

```bash
pytest -q
```

For graph-level validation:

```bash
python -m tests.test_graph_sufficient
python -m tests.test_graph_conflict
python -m tests.test_graph_clarification
```

## Project Structure

```text
evidence-graph/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ graph/
â”‚   â”‚   â”œâ”€â”€ nodes.py
â”‚   â”‚   â”œâ”€â”€ state.py
â”‚   â”‚   â””â”€â”€ workflow.py
â”‚   â”œâ”€â”€ embedding/
â”‚   â”œâ”€â”€ retrieval/
â”‚   â”œâ”€â”€ generation/
â”‚   â”œâ”€â”€ llm/
â”‚   â”œâ”€â”€ api/
â”‚   â””â”€â”€ utils/
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ corpus.jsonl
â”‚   â””â”€â”€ embeddings.db
â”œâ”€â”€ tests/
â”‚   â”œâ”€â”€ test_graph_sufficient.py
â”‚   â”œâ”€â”€ test_graph_conflict.py
â”‚   â”œâ”€â”€ test_graph_clarification.py
â”‚   â””â”€â”€ ...
â”œâ”€â”€ build_embeddings.py
â”œâ”€â”€ requirements.txt
â””â”€â”€ README.md
```

## Current Limitations

### Fact-level conflict detection

Conflict detection is currently specialized around pressure-related values. It should be generalized to compare facts relevant to the actual query attribute.

For example, pressure values in a document should not create a conflict when the user is asking about temperature.

### Structured knowledge

The current retrieval layer is primarily semantic/vector-based. A structured knowledge layer with entities, facts, and relations is planned:

```text
                    â”Œâ”€â”€ Semantic Embedding
Document â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
                    â””â”€â”€ Structure Extraction
                              â†“
                    Entities / Facts / Relations
```

### Hybrid retrieval

Future versions can combine semantic similarity, keyword matching, entity matching, structured fact retrieval, and contextual retrieval.

### Persistence / Sessions

The graph state is structured for future persistence and continuation, but full LangGraph checkpoint/session persistence is not yet part of V0.

## Roadmap

1. Embedding persistence â€” completed
2. Baseline retrieval â€” completed
3. Query analysis â€” completed
4. Query decomposition â€” completed
5. LangGraph orchestration â€” completed
6. Evidence aggregation â€” completed
7. Entity-based evidence filtering â€” completed
8. Evidence status routing â€” completed
9. Grounded answer generation â€” completed
10. Conflict-aware generation â€” completed
11. Insufficient-evidence clarification â€” completed
12. Generalize fact-level conflict detection
13. Structured knowledge extraction / NER
14. MongoDB structured evidence store
15. Semantic + structured evidence fusion
16. Hybrid retrieval
17. Evaluation and regression benchmark
18. Persistent LangGraph sessions/checkpoints
19. Dockerized deployment

## Development Principle

The project is intentionally being developed as an Evidence Graph rather than as a standalone generic chatbot.

The LLM is used for language understanding and grounded response generation, while retrieval, evidence filtering, status detection, and workflow routing remain explicit and inspectable components.

This separation makes the system easier to evaluate, debug, extend, and integrate with future expert/agent execution layers.