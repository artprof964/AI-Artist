# T16 Knowledge Agent Retrieval Validation

## Scope

Validated Knowledge Agent retrieval for T16:

> Retrieval test ingests sample source data, embeds it, queries Qdrant, and
> returns source-cited results through the Knowledge Agent.

The implementation is deterministic and local. It uses a swappable vector store
protocol plus `InMemoryQdrantVectorStore`, a Qdrant-like test double that models
collection `upsert` and `search` semantics without requiring external Qdrant or
network availability.

## Changed Behavior

- Added `backend.knowledge.KnowledgeAgent` for approved local source ingestion
  and retrieval.
- Added `DeterministicEmbeddingModel` for offline, repeatable embeddings.
- Added `InMemoryQdrantVectorStore` with collection-scoped point replacement and
  cosine similarity search sorted deterministically by score and point id.
- Added source-cited `KnowledgeAgentResponse` results and conversion to
  `SubAgentOutput` for the `knowledge` agent.
- Restricted ingestion to documents marked `approved=True`; unapproved sample
  data is neither embedded nor returned.
- Kept T16 bounded to retrieval over approved sample data; no T17+ image
  adapter, provenance, publishing, or external side-effect behavior was added.

## Focused Validation

```text
.\.venv\Scripts\python.exe -m pytest tests\test_knowledge_agent.py -q -p no:cacheprovider

3 passed in 0.10s
```

```text
.\.venv\Scripts\python.exe -m ruff check backend\knowledge.py tests\test_knowledge_agent.py

All checks passed!
```

Covered cases:

- approved sample source data is embedded and upserted into the vector store
- unapproved sample data is excluded from ingestion and retrieval
- disapproved vector-store hits are filtered even if present in the collection
- a query searches the Qdrant-like collection and returns the relevant source
- results include source id, title, URI, snippet, score, and citation
- Knowledge Agent output is valid `SubAgentOutput` with cited sources
- upserting an existing point id replaces the stored point deterministically

## Full Validation

```text
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider

88 passed, 1 skipped, 1 warning in 42.50s
```

```text
.\.venv\Scripts\python.exe -m ruff check .

All checks passed!
```
