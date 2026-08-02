# API registry

> **Purpose:** every HTTP endpoint the project exposes — implemented or planned — so an agent
> never redesigns an endpoint that's already specified, and never duplicates a route.
> **Who updates it:** whoever implements, changes, or removes an endpoint.
> **When it's updated:** in the same session as the code change (`SHUTDOWN.md` step 3), not
> deferred.
> **Read by:** any agent touching `src/rag_eval/api/`.

## Status: not yet implemented

No API code exists (`src/rag_eval/api/` holds only `.gitkeep`, milestone M6). The table below is
the **planned contract** from `docs/product/prd.md` (FR-11) — implementing against it satisfies
the requirement without re-deriving the endpoint list; deviating from it needs a `DECISIONS.md`
entry, not a silent change.

## Planned endpoints

| Method | Path | Purpose | Request | Response | Status |
|---|---|---|---|---|---|
| `POST` | `/query` | Full RAG: retrieve → rerank → (compress) → generate | question, optional config overrides | answer + cited context + timings | planned (M6) |
| `POST` | `/retrieve` | Retrieval only, no generation | question, strategy/config | ranked passages + scores | planned (M6) |
| `POST` | `/evaluate` | Trigger an evaluation run (single config or a matrix) | experiment config reference | run ID / MLflow link | planned (M6) |
| `GET` | `/health` | Liveness/readiness | — | service + dependency status (Qdrant/Weaviate/MLflow/Bedrock reachability) | planned (M6) |

## Conventions to follow once implemented

- Async endpoints (FastAPI, per `ARCHITECTURE.md` / ADR 0005).
- Request/response bodies are Pydantic v2 models — reuse the config models from
  `src/rag_eval/config/` rather than redefining shapes.
- Every endpoint's OpenAPI/Swagger docs (`/docs`) are the generated, authoritative API reference
  for external consumers — this file is the pre-implementation contract and the change log, not
  a replacement for the generated docs once they exist.
- Version the contract here before changing it in code: update this table's `Status` column and
  add a row to `MIGRATIONS.md` if the change is breaking (renamed field, removed endpoint).

## History

| Date | Change | Session |
|---|---|---|
| 2026-07-29 | Initial planned contract recorded (no implementation yet) | `sessions/2026-07-29-1940-claude-code.md` |
