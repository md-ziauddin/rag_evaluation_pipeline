# Tasks

> **Purpose:** the live task board — what's done, in progress, blocked, or next. The detailed
> checklist-level breakdown lives in `docs/planning/task-breakdown.md` (local, gitignored); this
> file tracks *live status* against that breakdown, plus anything that comes up outside it.
> **Who updates it:** every agent, whenever a task changes state — not just at shutdown.
> **When it's updated:** the moment a task moves state (starts, blocks, finishes), and again at
> `SHUTDOWN.md` step 1 as a final check.
> **Read by:** every agent, step 1 of `BOOTSTRAP.md` (filtered to `IN_PROGRESS`/`BLOCKED`).

State machine for every row: `BACKLOG → READY → IN_PROGRESS → IN_REVIEW → DONE`, with `BLOCKED`
and `ABANDONED`/`SUPERSEDED` as side states. Full definitions in `STATE.md`.

## Epics (mirrors `docs/planning/task-breakdown.md` and `docs/planning/roadmap.md`)

| Epic | Milestone | Status | Notes |
|---|---|---|---|
| E0 — Environment & scaffolding | M0 | **DONE** | Repo tree, config stubs, CI, compose file. See `FILE_INDEX.md`. |
| E0.5 — Design documentation | M0.5 | **DONE** | 19-section design set in `docs/` (gitignored). |
| E0.6 — AI operating system | M0.6 | **DONE** | This `.ai/` system. Session: `sessions/2026-07-29-1940-claude-code.md`. |
| E1 — Dataset pipeline | M1 | **READY** | Not started. See active tasks below. |
| E2 — Chunking | M2 | **BACKLOG** | Depends on E1. |
| E3 — Embedding providers | M3 | **BACKLOG** | Depends on E2. |
| E4 — Vector stores, indexing, native hybrid | M4 | **BACKLOG** | Depends on E3. Largest single epic (XL). |
| E5 — Retrievers and rerankers | M5 | **BACKLOG** | Depends on E3, E4. |
| E6 — Generation, RAG orchestration, API | M6 | **BACKLOG** | Depends on E5. |
| E7 — Evaluation framework + MLflow | M7 | **BACKLOG** | Depends on E6. |
| E8 — Experiment runner + matrix | M8 | **BACKLOG** | Depends on E7. |
| E9 — Hardening + v1.0 | M9 | **BACKLOG** | Depends on E8. |

## Active tasks (the actual next work)

| ID | Task | Status | Owner | Blocked on |
|---|---|---|---|---|
| PRE-1 | Verify `docker compose config` / `make up` actually bring up Qdrant, Weaviate, MLflow in this environment | **READY** | — | — |
| PRE-2 | Confirm AWS Bedrock model access enabled for target account/region | **READY** | — | AWS account access (project owner) |
| T1.1 | PubMedQA + MedQA loaders, normalize to common document schema | **BACKLOG** | — | PRE-1 |
| T1.2 | Build retrieval corpus + PubMedQA qrels from `contexts`; MedQA MCQ set | **BACKLOG** | — | T1.1 |
| T1.3 | Content-hash versioning of processed dataset outputs | **BACKLOG** | — | T1.2 |

Full checklist for every task under every epic (T2.1, T3.1, ... through T9.3): see
`docs/planning/task-breakdown.md`. This file is not a duplicate of that checklist — it's the
live status layer on top of it. When a task there gets picked up, add a row here; when it's
done, mark it here and leave the checklist doc as the historical record of scope.

## Completed (condensed — session files have the full detail)

| ID | Task | Completed | Session |
|---|---|---|---|
| E0 | Full repo scaffold (dirs, `pyproject.toml`, `docker-compose.yml`, CI, config examples) | 2026-07-29 | `sessions/2026-07-29-1500-claude-code.md` |
| E0.5 | 19-section design documentation set | 2026-07-29 | `sessions/2026-07-29-1500-claude-code.md` |
| E0.6 | `.ai/` operating system (this system) | 2026-07-29 | `sessions/2026-07-29-1940-claude-code.md` |

## Abandoned / superseded

None yet.

## Rules for this file

- A task moves to `IN_PROGRESS` the moment you start it, not retroactively at shutdown — another
  agent could start the same task in a different tool mid-session otherwise.
- Never mark `DONE` without a matching `FILE_INDEX.md` update for everything the task touched
  (`RULES.md` #6).
- If you pick up a task not listed here (something outside `task-breakdown.md`'s scope), add a
  row under Active tasks with a new ID before starting — don't do untracked work.
