# Changelog

> **Purpose:** a human- and agent-readable record of what changed, in the style of
> [Keep a Changelog](https://keepachangelog.com/) — one line per user-visible or agent-visible
> change, grouped by release/session batch.
> **Who updates it:** every agent, at `SHUTDOWN.md` step 6, for anything behavior- or
> interface-visible. Skip pure internal refactors with no external effect.
> **When it's updated:** every session with a meaningful change, before the session ends.
> **Read by:** anyone (human or agent) trying to understand what happened without reading every
> session file.

Format: `Added` / `Changed` / `Fixed` / `Removed`, under `Unreleased` until a version is tagged
(per `docs/planning/roadmap.md`'s milestones — this project versions by milestone, not by
semver, until v1.0).

## [Unreleased]

### Added

- Repository scaffold: `src/rag_eval/` package skeleton (12 subpackages, empty), `pyproject.toml`
  with dependency groups, `requirements/{base,dev}.txt`, `.env.example`, `docker-compose.yml`
  (Qdrant + Weaviate + MLflow functional, `api` service placeholder), `Makefile`,
  `.github/workflows/ci.yml`, `config/{settings,experiment}.example.yaml`.
- Full 19-section design documentation set under `docs/` (product, architecture + 12 ADRs,
  retrieval, evaluation, planning, engineering, risks) — gitignored, present locally.
- `.ai/` operating system: cross-agent tracking (`STATE.md`, `TASKS.md`, `FILE_INDEX.md`,
  `ARCHITECTURE.md`, `API.md`, `DATABASE.md`, `MIGRATIONS.md`, `DECISIONS.md`, `PROMPTS.md`),
  bootstrap/shutdown procedures, session log, templates, automation scripts, and cross-tool
  pointer files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursorrules`).

### Changed

- Renamed the original top-level `README.md` planning draft to `Plan.md`; wrote a new
  `README.md` for the scaffolded repo. `Plan.md` and `docs/` gitignored per project owner
  request.
- **Replaced LangChain with LangGraph as the orchestration framework**, before any
  implementation existed. Every `langchain-*` dependency removed from `pyproject.toml`; every
  retrieval strategy in `docs/retrieval/retrieval-pipeline.md` reframed as a hand-rolled
  LangGraph node/function over direct `boto3`/`qdrant-client`/`weaviate-client` calls instead of
  a framework retriever class. New `docs/architecture/adr/0013-langgraph-replaces-langchain.md`
  supersedes `0001`. 18 files touched in total (14 flagged by the initial scoping grep + the new
  ADR + 3 references the literal-string grep missed because they named the LangChain class
  `ChatBedrockConverse` without the word "langchain" nearby); see
  `sessions/2026-07-29-2015-claude-code.md`.

### Fixed

- Nothing yet — no implementation exists to have bugs.

### Removed

- Nothing yet.

## History

No tagged releases yet. First tag expected at v1.0 (milestone M9), per
`docs/planning/roadmap.md`.
