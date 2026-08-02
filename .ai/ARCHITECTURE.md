# Architecture constraints

> **Purpose:** the compressed list of technical decisions already locked in, so no agent
> re-derives or re-litigates them from scratch. This is an index into `docs/architecture/adr/`
> (full reasoning, alternatives considered, consequences) — not a replacement for it.
> **Who updates it:** an agent, only after a new ADR is written in `docs/architecture/adr/` or
> an existing one is superseded. Never edit this file without a corresponding ADR change.
> **When it's updated:** whenever an ADR is added, changed, or superseded.
> **Read by:** every agent, step 5 of `BOOTSTRAP.md`.

## System shape (one paragraph)

One codebase serves two purposes: an offline evaluation harness (builds indexes, runs the
comparison matrix) and an online RAG service (answers questions with whichever configuration was
promoted). They share the same core modules — chunking, embedding, vector stores, retrievers,
rerankers, generation — behind provider interfaces, so what gets measured is exactly what gets
served. Full diagrams: `docs/architecture/system-architecture.md`.

## Locked-in decisions (ADR index)

| # | Decision | One-line reason | Full record |
|---|---|---|---|
| 0001 | ~~LangChain as orchestration framework~~ | **Superseded by 0013.** Kept for historical reasoning only. | `docs/architecture/adr/0001-langchain-vs-llamaindex.md` |
| 0002 | Qdrant as a compared vector DB | Native hybrid (RRF/DBSF fusion), sparse vectors, payload filtering | `docs/architecture/adr/0002-qdrant.md` |
| 0003 | Weaviate as a compared vector DB | Distinct native hybrid mechanism (`alpha`-weighted BM25+vector) | `docs/architecture/adr/0003-weaviate.md` |
| 0004 | Docker Compose for local orchestration | Databases must be containerized, not host-installed; K8s deferred | `docs/architecture/adr/0004-docker-compose.md` |
| 0005 | FastAPI for the service layer | Async fits I/O-bound Bedrock/DB calls; Pydantic validation + OpenAPI free | `docs/architecture/adr/0005-fastapi.md` |
| 0006 | Pytest as test framework | Markers separate fast (unit) from slow (integration/e2e) paths | `docs/architecture/adr/0006-pytest.md` |
| 0007 | Bedrock default behind a provider abstraction | Reconciles "Bedrock default" with "OSS benchmarked" via `EmbeddingProvider`/`LLMProvider`/`Reranker` interfaces | `docs/architecture/adr/0007-bedrock-default-and-provider-abstraction.md` |
| 0008 | Embedding model set: Titan v2 default + BGE/E5/GTE/Nomic/Instructor/medical benchmark | Domain fit (medical) is a first-class variable, not an afterthought | `docs/architecture/adr/0008-embedding-model-selection.md` |
| 0009 | Reranker set: Bedrock rerank default + bge-reranker-v2-m3/MiniLM/medical cross-encoder | Reranking is the largest cheap quality lever; measured as its own stage | `docs/architecture/adr/0009-reranker-selection.md` |
| 0010 | MLflow for experiment tracking | Self-hosted, open-source, system of record; LangSmith optional for tracing only | `docs/architecture/adr/0010-experiment-tracking-mlflow.md` |
| 0011 | `ranx` + `ragas` for evaluation | Two distinct metric layers (IR vs. answer quality) need two distinct, correct tools | `docs/architecture/adr/0011-evaluation-libraries.md` |
| 0012 | PubMedQA → IR metrics, MedQA → end-to-end MCQ accuracy | MedQA has no per-passage relevance labels; treating them the same fabricates rigor | `docs/architecture/adr/0012-dataset-roles.md` |
| 0013 | **LangGraph replaces LangChain entirely** (supersedes 0001) | Every retrieval strategy hand-built as a LangGraph node/function over raw Bedrock/Qdrant/Weaviate SDKs — no framework retriever classes, decided before implementation began | `docs/architecture/adr/0013-langgraph-replaces-langchain.md` |

If `docs/architecture/adr/` isn't present in your checkout, the "one-line reason" column above is
the working constraint — treat it as binding until you can read the full record.

**A note on how 0013 got there:** it started as a scoping question the project owner asked
("how many files do I need to update to swap LangChain for LangGraph?"), which surfaced a real
fork — LangGraph on top of LangChain's components vs. a full replacement — that materially
changed the size of the change. The owner was asked to pick, chose full replacement, and that
answer became this ADR. This is `BOOTSTRAP.md` step 9 and `RULES.md` #12 working as intended:
the ambiguity was surfaced and resolved before 14 files got edited on a guess.

## Constraints that aren't ADRs but are still binding

- **No host-installed databases.** Everything runs in Docker Compose containers.
- **Bedrock model IDs carry a provider prefix** (`amazon.titan-embed-text-v2:0`,
  `anthropic.claude-sonnet-5`, `amazon.rerank-v1:0`/`cohere.rerank-v3-5`). Verify exact IDs,
  regional availability, and pricing against current AWS docs before hard-coding them anywhere —
  see `docs/architecture/configuration-management.md`.
- **`src/` layout.** The package is only importable once installed (`pip install -e .`); tests
  never import from the working tree directly.
- **Secrets only from `.env`**, never from YAML in `config/`, never hard-coded.
- **Vectors are supplied externally to Weaviate** (`DEFAULT_VECTORIZER_MODULE=none`) — both
  databases receive vectors from the same `EmbeddingProvider`, so the comparison is about
  indexing/retrieval, not differing built-in vectorizers.

## What to do if a task seems to require breaking one of these

Don't. Write a `DECISIONS.md` entry proposing the change, with the same rigor as the ADR it
would supersede (alternatives considered, consequences), and get it confirmed before acting on
it. See `RULES.md` #4.
