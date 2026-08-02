# Current state

> **Purpose:** the single answer to "where are we right now" — one file, always current. If
> this file and any other file disagree about current status, this file is wrong and needs
> fixing, not the other one.
> **Who updates it:** every agent, at the end of every session (`SHUTDOWN.md` step 4). Also
> mid-session if a blocker changes.
> **When it's updated:** every session that changes project state, without exception.
> **Read by:** every agent, step 1 of `BOOTSTRAP.md` (second file after `PROJECT.md`).

---

**Last updated:** 2026-07-29, 20:15 — by Claude Code (session
`sessions/2026-07-29-2015-claude-code.md`)

## Project-level state (milestone)

Milestones M0–M9 are defined in `docs/planning/roadmap.md` (local, gitignored). This file
tracks *live position* against them — read the roadmap doc for what each milestone means, read
this section for where we actually are.

| Milestone | Status |
|---|---|
| M0 — Environment & scaffolding | **Done.** Repo tree, `pyproject.toml`, `docker-compose.yml`, CI workflow, config examples, `.env.example` all exist. Package dirs under `src/rag_eval/` are empty (`.gitkeep` only) — this is the scaffold, not the implementation. |
| M0.5 — Design documentation | **Done.** Full 19-section design set written to `docs/` (gitignored, present locally). |
| M0.6 — AI-OS (this system) | **Done.** `.ai/` created this session. |
| M1 — Dataset pipeline | **Not started.** No loaders, no corpus builder, no PubMedQA qrels exist yet. |
| M2–M9 | **Not started.** |

**Current phase:** between M0 and M1. Scaffolding and design are complete; no application code
exists yet. The `docker-compose.yml` stack (Qdrant, Weaviate, MLflow) has not been verified to
actually start in this environment — that's the first thing to check before M1 work begins.

**Architecture note (2026-07-29):** the orchestration framework changed from LangChain to
**LangGraph** — a full replacement, not an addition — before any implementation began. See
`ARCHITECTURE.md` ADR 0013 (supersedes ADR 0001). If you have any prior context assuming
LangChain retriever classes (`EnsembleRetriever`, `MultiQueryRetriever`, etc.), it's stale —
every strategy in `docs/retrieval/retrieval-pipeline.md` is now hand-built.

## Blocked on

Nothing is actively blocking. Before M1 starts, confirm:
- Docker is available and `docker compose config` / `make up` actually work here.
- AWS Bedrock model access is enabled for the target account/region (Titan v2, Claude, rerank
  model) — this is a prerequisite noted in `docs/planning/implementation-plan.md` Phase 0 and
  has not yet been verified.

## Next actions (priority order)

1. Verify the Docker Compose stack starts cleanly (`make up`; check Qdrant/Weaviate/MLflow
   health).
2. Confirm Bedrock model access, per `docs/architecture/adr/0007-bedrock-default-and-provider-abstraction.md`.
3. Begin M1 (dataset pipeline): PubMedQA + MedQA loaders, corpus builder, PubMedQA qrels. See
   `.ai/TASKS.md` epic E1 / `docs/planning/task-breakdown.md`.

## Task-level state machine

Every task in `.ai/TASKS.md` moves through these states (this is separate from the
project-level milestone table above — a project is "in M1"; a single task is "IN_PROGRESS"):

```
BACKLOG → READY → IN_PROGRESS → IN_REVIEW → DONE
              ↘ BLOCKED ↗              ↘ ABANDONED / SUPERSEDED
```

- **BACKLOG** — known, not yet ready to start (may depend on an earlier task).
- **READY** — unblocked, could be picked up next session.
- **IN_PROGRESS** — a session is actively working it.
- **BLOCKED** — started, can't continue without something external (a decision, a credential,
  a failing dependency). Note the blocker in the task's row.
- **IN_REVIEW** — code/docs exist, not yet confirmed correct (tests not run, output not
  eyeballed).
- **DONE** — confirmed complete; `FILE_INDEX.md` updated for everything it touched.
- **ABANDONED** — deliberately not doing this; say why.
- **SUPERSEDED** — replaced by a different task/decision; link to the replacement.

## Consistency check

Per `SHUTDOWN.md` step 8: this file's milestone table should never claim a milestone as further
along than `TASKS.md`'s aggregate state supports. As of this update, both agree: M0 done, M1 not
started.
