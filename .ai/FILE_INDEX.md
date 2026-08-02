# File index

> **Purpose:** the registry of every meaningful file in the repo — what it's for, whether it's
> safe to edit, and whether it's been deprecated. This is what stops an agent from recreating a
> file that already exists, or editing one it shouldn't.
> **Who updates it:** every agent, for every file it creates or meaningfully modifies.
> **When it's updated:** immediately when a file is created (not deferred to shutdown), and at
> `SHUTDOWN.md` step 2 as a final pass for anything missed.
> **Read by:** every agent, step 4 of `BOOTSTRAP.md`, before creating any file.

**Not every file in the repo needs a row.** Register: anything with a non-obvious purpose,
anything another file depends on, anything a future agent might be tempted to recreate. Skip:
`.gitkeep` placeholders (tracked once, as a directory note below), generated/build artifacts,
and files whose purpose is self-evident from a one-line docstring at the top.

Columns: **Status** ∈ {scaffold, implemented, deprecated, deleted} · **Safe to edit** ∈
{yes, ask-first, no — see notes}.

## Root

| File | Purpose | Owner module | Status | Created by | Last modified | Depends on | Consumed by | Safe to edit | Deprecated | Replace with |
|---|---|---|---|---|---|---|---|---|---|---|
| `README.md` | Project overview, quickstart, doc links | — | implemented | claude-code | 2026-07-29 | — | new contributors | yes | no | — |
| `Plan.md` | Original planning artifact (renamed from README draft) | — | implemented | project owner | 2026-07-29 | — | project owner only | ask-first | no | — |
| `pyproject.toml` | Package metadata, deps (`local`/`eval`/`medical`/`dev` extras), ruff/mypy/pytest config | — | scaffold | claude-code | 2026-07-29 | — | every module, CI | yes | no | — |
| `requirements/base.txt` | Mirrors `pyproject.toml` runtime deps (`pip install -e .`) | — | scaffold | claude-code | 2026-07-29 | `pyproject.toml` | Docker build (future) | yes | no | — |
| `requirements/dev.txt` | Mirrors `pyproject.toml` dev+eval extras | — | scaffold | claude-code | 2026-07-29 | `pyproject.toml` | CI, local dev | yes | no | — |
| `.env.example` | Every env var the config layer reads | — | scaffold | claude-code | 2026-07-29 | — | `src/rag_eval/config` (not yet built) | yes | no | — |
| `.gitignore` | Excludes venvs, caches, data, secrets, `docs/`, `Plan.md` | — | implemented | claude-code + project owner | 2026-07-29 | — | git | ask-first (project owner added `docs/`/`Plan.md` rules intentionally — don't revert) | no | — |
| `.dockerignore` | Keeps build context small/secret-free | — | scaffold | claude-code | 2026-07-29 | — | future Docker builds | yes | no | — |
| `docker-compose.yml` | Qdrant, Weaviate, MLflow (functional); `api` service (commented placeholder) | — | scaffold | claude-code | 2026-07-29 | — | `make up`, integration tests (future) | yes | no | — |
| `Makefile` | `up/down/lint/format/typecheck/test/eval/security` targets | — | scaffold | claude-code | 2026-07-29 | `docker-compose.yml`, `pyproject.toml` | developers, CI | yes | no | — |
| `.github/workflows/ci.yml` | Lint/format/type/unit/security/compose-validate jobs, permissive until code lands | — | scaffold | claude-code | 2026-07-29 | `pyproject.toml` | GitHub Actions | yes | no | — |
| `.ai/` | This operating system (18 files + `sessions/`/`checkpoints/`/`templates/`/`scripts/`) | — | implemented | claude-code | 2026-07-29 | — | every agent | see `.ai/RULES.md` | no | — |
| `docs/architecture/adr/0013-langgraph-replaces-langchain.md` | ADR: LangGraph replaces LangChain entirely, supersedes ADR 0001 | — | implemented | claude-code | 2026-07-29 | ADR 0001, ADR 0007 | `.ai/ARCHITECTURE.md`, `docs/retrieval/retrieval-pipeline.md`, all future orchestration code | yes | no | — |
| `AGENTS.md` | Generic cross-tool entry point → redirects to `.ai/BOOTSTRAP.md` | — | implemented | claude-code | 2026-07-29 | `.ai/BOOTSTRAP.md` | Codex and other AGENTS.md-reading tools | yes | no | — |
| `CLAUDE.md` | Claude Code entry point → redirects to `.ai/BOOTSTRAP.md` | — | implemented | claude-code | 2026-07-29 | `.ai/BOOTSTRAP.md` | Claude Code (auto-read) | yes | no | — |
| `GEMINI.md` | Gemini CLI entry point → redirects to `.ai/BOOTSTRAP.md` | — | implemented | claude-code | 2026-07-29 | `.ai/BOOTSTRAP.md` | Gemini CLI (auto-read) | yes | no | — |
| `.cursorrules` | Cursor entry point → redirects to `.ai/BOOTSTRAP.md` | — | implemented | claude-code | 2026-07-29 | `.ai/BOOTSTRAP.md` | Cursor (auto-read) | yes | no | — |
| `.vscode/tasks.json` | VS Code tasks: show state, new/end session, validate index, compose up | — | implemented | claude-code | 2026-07-29 | `.ai/scripts/*` | VS Code task runner | yes | no | — |

## `config/`

| File | Purpose | Status | Created by | Depends on | Consumed by | Safe to edit |
|---|---|---|---|---|---|---|
| `config/settings.example.yaml` | Runtime settings schema (providers, chunking, retrieval, vectorstores, tracking) | scaffold | claude-code | — | future `src/rag_eval/config` | yes |
| `config/experiment.example.yaml` | Experiment-matrix schema for the future runner | scaffold | claude-code | `settings.example.yaml` conventions | future `src/rag_eval/experiments` | yes |

## `src/rag_eval/` — package skeleton

All twelve subpackages below currently contain **only `.gitkeep`** — no implementation exists.
Do not create implementation files here without first checking `TASKS.md`'s active list; each
one is scoped to a specific milestone.

| Package | Will own | Target milestone | Status |
|---|---|---|---|
| `config/` | Typed settings models (pydantic-settings), YAML+env loading | M0 (partially — the package itself is scaffolded; the models aren't written) | scaffold |
| `ingestion/` | HF dataset loaders, normalization, corpus/qrels builders | M1 | scaffold |
| `chunking/` | Chunker interface + implementations, metadata schema | M2 | scaffold |
| `embeddings/` | `EmbeddingProvider` interface, Bedrock + local implementations | M3 | scaffold |
| `vectorstores/` | Qdrant/Weaviate adapters, native hybrid, payload indexing | M4 | scaffold |
| `retrievers/` | Dense/sparse/hybrid/ensemble/multi-query/self-query/parent-doc/compression | M5 | scaffold |
| `rerankers/` | `Reranker` interface, Bedrock + cross-encoder implementations | M5 | scaffold |
| `generation/` | `LLMProvider` interface, Bedrock + local LLMs, prompt templates | M6 | scaffold |
| `evaluation/` | IR metrics (ranx), ragas answer metrics, systems metrics | M7 | scaffold |
| `experiments/` | Matrix expansion, run orchestration, MLflow logging | M8 | scaffold |
| `api/` | FastAPI app, routers, request/response models | M6 | scaffold |
| `utils/` | Logging, timing, hashing, caching, MLflow helpers | cross-cutting | scaffold |

## `tests/`

| Dir | Purpose | Status |
|---|---|---|
| `tests/unit/` | Fast, no external services | scaffold — no tests written yet |
| `tests/integration/` | Against dockerized Qdrant/Weaviate (testcontainers) | scaffold |
| `tests/e2e/` | Full pipeline on a tiny fixture corpus | scaffold |

## `data/`, `experiments/`, `notebooks/`, `scripts/`

All four contain only `.gitkeep` — gitignored contents by design (`RULES.md` #9). Do not add
rows here per-file; these directories never hold tracked, meaningfully-named files.

## `docs/` (gitignored, present locally)

Full design set — see `docs/README.md` for its own index. Not duplicated here; this repo's
`FILE_INDEX.md` tracks the tracked (git) surface plus `.ai/`. If you're working from a checkout
where `docs/` is absent, everything referenced from it in `PROJECT.md`/`ARCHITECTURE.md` is
still summarized there — you're missing the full rationale, not the constraints.

## How to keep this file honest

- New file → new row, same session, not deferred.
- Deprecating something → flip the `Deprecated`/`Replace with` columns, keep the row.
- If you're unsure whether a file is "meaningful" enough to register: if the next agent could
  plausibly try to recreate it, register it.
