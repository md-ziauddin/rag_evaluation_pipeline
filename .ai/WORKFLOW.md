# Example workflow

> **Purpose:** a concrete, worked walkthrough of the whole system — bootstrap, work, shutdown,
> handoff to a different agent in a different tool — so the abstract procedures in
> `BOOTSTRAP.md`/`SHUTDOWN.md` are visibly correct rather than theoretical.
> **Who updates it:** the project owner, or an agent that finds the example has gone stale
> relative to how the system actually works.
> **When it's updated:** when a procedure changes in a way that makes this example misleading.
> **Read by:** anyone new to the system who wants to see it work before trusting it.

## Scenario

Session 1 (Claude Code) built the scaffold and design docs and — this session — the `.ai/`
system itself. Session 2, hypothetically, is **Gemini CLI**, picking up milestone M1 (dataset
pipeline) a week later, on the same machine, with zero memory of sessions 1 or the reasoning
behind any of it.

## What Gemini CLI does

**Bootstrap** (`BOOTSTRAP.md`):

1. Reads `PROJECT.md` — learns this is a medical RAG comparison harness, Bedrock-default,
   containerized Qdrant+Weaviate, and that PubMedQA/MedQA have different evaluation roles.
2. Reads `STATE.md` — learns M0 is done, M1 is next, and the two pre-M1 checks (Docker Compose
   actually starts; Bedrock access confirmed) haven't been verified yet.
3. Reads `TASKS.md`, filters to `READY`/`IN_PROGRESS` — sees `PRE-1`, `PRE-2`, and `T1.1`–`T1.3`
   waiting, all `BACKLOG`/`READY`, none claimed.
4. Reads `ARCHITECTURE.md` — notes the locked-in stack and, specifically, ADR 0012 (PubMedQA →
   IR metrics, MedQA → accuracy) before touching anything dataset-related.
5. Greps `FILE_INDEX.md` for anything ingestion-related — finds `src/rag_eval/ingestion/`
   scaffolded but empty. Nothing to avoid recreating yet; this is genuinely new work.

**Summarizes and plans** (steps 7–8): states back that it understands the task as building the
PubMedQA/MedQA loaders and the qrels builder (T1.1–T1.3), notes the two prerequisite checks
haven't been done, and proposes doing `PRE-1` (verify `make up` works) before writing any
ingestion code, since T1.x doesn't strictly need it but the next milestone will.

**No ambiguity found** — proceeds without asking.

**Works:** runs `make up`, confirms Qdrant/Weaviate/MLflow come up healthy, marks `PRE-1` `DONE`
in `TASKS.md`. Starts `T1.1`, marks it `IN_PROGRESS`, writes the PubMedQA and MedQA loaders under
`src/rag_eval/ingestion/`.

**Hits something worth logging:** discovers MedQA's Hugging Face loader needs
`trust_remote_code=True`, which isn't mentioned anywhere yet. This is a security-relevant,
non-obvious fact — not a full ADR (nothing architectural changed), so it goes in `DECISIONS.md`
as a quick entry.

**Shutdown** (`SHUTDOWN.md`):

1. `TASKS.md`: `PRE-1` → `DONE`. `T1.1` → `IN_REVIEW` (loaders written, not yet tested against
   the real corpus size).
2. `FILE_INDEX.md`: adds rows for the two new loader files, notes dependencies
   (`datasets`, `huggingface-hub`) and consumers (future corpus builder).
3. `DECISIONS.md`: logs the `trust_remote_code` finding.
4. `STATE.md`: updates "Next actions" to reflect `T1.1` is in review, not done; "Blocked on"
   stays clear since nothing external is stopping progress.
5. Proposes a commit message with the `AI-Session:` trailer.
6. `CHANGELOG.md`: adds an `Added` line for the two loaders under `Unreleased`.
7. Writes `sessions/2026-08-05-1015-gemini-cli.md` with the full detail (files touched, the
   `trust_remote_code` finding, what's left: testing the loaders against the real dataset size).
8. Adds a row to `SESSION_LOG.md`.
9. Final check: `STATE.md` says "M1 in progress, T1.1 in review" and `TASKS.md` agrees — no
   contradiction to fix.

## What Claude Code sees next time, in a different tool entirely

Whether it's Claude Code again, or Codex, or Cursor: `BOOTSTRAP.md` step 1–3 immediately surfaces
that `T1.1` is `IN_REVIEW` (not `DONE`, not `BACKLOG`) and that `DECISIONS.md` has a fresh entry
about `trust_remote_code`. No agent re-writes the MedQA loader from scratch, and none of them
re-discovers the `trust_remote_code` requirement the hard way.

## The property this demonstrates

Nothing in this handoff depended on Gemini CLI and the next agent being the same tool, sharing a
conversation, or the human re-explaining anything. Every fact either agent needed was sitting in
a file with exactly one job.
