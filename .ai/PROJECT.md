# Project identity

> **Purpose:** the static facts about this project that almost never change — what it is,
> what it explicitly is not, the fixed stack, and the hard constraints. Read this once per
> session; don't re-derive it from the codebase.
> **Who updates it:** the project owner, or an agent after the owner confirms a change to one
> of these fixed facts (a genuine stack swap, a scope change to the non-goals).
> **When it's updated:** rarely — only when something on this page actually changes, not every
> session.
> **Read by:** every agent, step 1 of `BOOTSTRAP.md`.

## What this is

A production-grade RAG evaluation pipeline for the medical domain. It is built to **rigorously
compare** retrieval strategies, vector databases, and embedding models on medical question
answering — not to ship one opinionated RAG stack. The comparison matrix and its evidence are
the deliverable as much as the running service is.

Full rationale: `docs/product/executive-summary.md` and `docs/product/prd.md` (local, gitignored
— present in this checkout, not guaranteed in every clone).

## What this explicitly is not

- Not a clinical decision-support tool. No output is medical advice.
- Not an embedding/LLM training project — models are used as-is in v1.
- Not a multi-domain search system — medical domain throughout.
- Not a UI product — v1 ships an API and a comparison report, not an end-user app.

## Fixed stack

| Layer | Choice | Why (one line) |
|---|---|---|
| Orchestration | LangGraph, over direct `boto3` (Bedrock) + `qdrant-client`/`weaviate-client` SDKs | Every retrieval strategy hand-built as a graph node — no framework retriever classes. Was LangChain until [ADR 0013](../docs/architecture/adr/0013-langgraph-replaces-langchain.md) superseded [ADR 0001](../docs/architecture/adr/0001-langchain-vs-llamaindex.md), decided before implementation began. |
| Vector databases | Qdrant **and** Weaviate, both containerized | Required comparison pair — two distinct native-hybrid mechanisms. |
| Embedding/LLM/rerank default | AWS Bedrock (Titan v2 / Cohere v3 embed; Claude via direct `boto3` `bedrock-runtime`; Bedrock rerank) | Project owner's chosen default provider, behind a swappable interface. |
| Open-source benchmark set | BGE, E5, GTE, Nomic, Instructor, + a medical encoder (MedCPT/PubMedBERT-based) | Benchmarked against Bedrock through the same provider interface, not a separate code path. |
| Orchestration/service | FastAPI + uvicorn | Requested; async fits I/O-bound Bedrock + DB calls. |
| Experiment tracking | MLflow, self-hosted in Docker Compose | Open-source preference; system of record for every run. |
| Evaluation | `ranx` (IR metrics) + `ragas` (answer metrics) | Two distinct metric layers, not one library doing both. |
| Testing | Pytest (unit/integration/e2e/regression/perf/load) | Requested. |
| CI | GitHub Actions | Requested. |
| Containerization | Docker Compose, no host-installed databases | Explicit requirement. |
| Packaging | `src/` layout, Python ≥3.11 | Prevents accidental working-tree imports. |

Full reasoning per choice, with alternatives considered: `docs/architecture/adr/` (12 records,
local, gitignored).

## Datasets and their distinct roles

- **PubMedQA** (RAG-formatted, MIT-licensed) — has per-question gold `contexts` → drives
  **retrieval IR metrics** (Precision@k, Recall@k, MRR, MAP, nDCG@k, Hit Rate).
- **MedQA** (USMLE-style MCQ + textbook corpus, license unverified) — **no** per-passage
  relevance labels → drives **end-to-end MCQ accuracy**, not passage IR metrics.

Do not report IR metrics on MedQA without first synthesizing and clearly labeling weak qrels —
this is a deliberate, recorded decision (see the architecture ADR index), not an oversight.

## Hard constraints (don't re-litigate without a `DECISIONS.md` entry)

- No PHI to Bedrock (or any external provider) without a signed BAA. Public datasets only, v1.
- No dataset, built index, or experiment artifact is ever committed to git.
- No vector database is installed on the host — containers only.
- Bedrock vs. open-source is always a config change, never a forked code path.
- Orchestration is LangGraph, not LangChain — every retrieval strategy is hand-built against
  the raw SDKs, not assembled from a framework retriever class (ADR 0013).
- `docs/` and `Plan.md` are gitignored by the project owner's choice — don't un-gitignore them.

## Where to go deeper

- System shape and data flow, with diagrams: `docs/architecture/system-architecture.md`.
- Repo layout rationale: `docs/architecture/folder-structure.md` (mirror of the real tree —
  see `.ai/FILE_INDEX.md` for the live, per-file version).
- Milestones M0–M9: `docs/planning/roadmap.md` — `.ai/STATE.md` tracks live position against it.
- Risks (medical, legal, evaluation-validity): `docs/risks/risks.md`.

If any of `docs/` is missing in your checkout, everything in this file and in
`.ai/ARCHITECTURE.md` still holds — it's the compressed version of that reasoning, not a summary
that depends on the source being present.
