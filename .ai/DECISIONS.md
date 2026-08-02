# Decisions log

> **Purpose:** a fast, low-ceremony record of decisions and their reasoning that don't (yet)
> warrant a full ADR in `docs/architecture/adr/`. Some entries here graduate to a formal ADR
> once they prove durable; most operational decisions never need to.
> **Who updates it:** any agent making a decision that isn't purely local to one task, or
> proposing a change to something `ARCHITECTURE.md` already locked in.
> **When it's updated:** the moment the decision is made, not retroactively.
> **Read by:** any agent about to make a decision that might already have been made, and step 9
> of `BOOTSTRAP.md` (checking whether ambiguity is actually already resolved here).

## When to write here vs. write a full ADR

Write here for: naming conventions, tool configuration choices, scope calls within an already-
decided architecture, anything reversible without much cost. Write a full ADR
(`docs/architecture/adr/NNNN-*.md`, with alternatives-considered and consequences) for: a new
external dependency, a change to `ARCHITECTURE.md`'s locked-in list, anything expensive to
reverse. If a decision here gets revisited more than once, promote it to an ADR instead of
re-litigating it in this file repeatedly.

## Log (most recent first)

### 2026-07-29 — LangGraph replaces LangChain entirely (promoted to ADR 0013)

**Decision:** dropped LangChain and every `langchain-*` package; LangGraph is now the sole
orchestration layer, with every retrieval strategy hand-built as a graph node/function over raw
`boto3`/`qdrant-client`/`weaviate-client`, per
`docs/architecture/adr/0013-langgraph-replaces-langchain.md` (supersedes ADR 0001).
**Reasoning:** the project owner asked how many files a LangChain→LangGraph swap would touch;
answering surfaced a real fork — LangGraph layered on top of LangChain's retriever/vectorstore
components vs. a full replacement — that changes the size of the change by roughly an order of
magnitude. Asked, and the owner chose full replacement. This is expensive enough to reverse
(rewrites ADR 0001, touches 15 files, changes M4/M5 complexity) that it was promoted straight to
a full ADR rather than staying a quick log entry — see this file's own header for that bar.
**Reversible:** yes, but not cheaply — reverting would mean re-adding every `langchain-*`
package and re-deriving the retriever-class-based strategy implementations this decision
replaced with hand-rolled ones. Decided before any implementation code existed, so today it's
still a documentation-only change; it stops being cheap the moment M4/M5 code is written against
it.

### 2026-07-29 — Treat `.ai/` as operational tracking, committed by default

**Decision:** `.ai/` is git-tracked (not gitignored like `docs/`/`Plan.md`), on the reasoning
that it holds operational state (what exists, what's in progress) rather than design rationale.
**Reasoning:** the project owner gitignored `docs/` and `Plan.md` specifically to keep deep
planning/thinking private from external viewers; `.ai/` intentionally avoids duplicating that
rationale (it points into `docs/` rather than repeating it) so it stays useful even if the
privacy boundary around `docs/` is reconsidered later.
**Reversible:** yes — gitignore `.ai/` the same way if this call turns out wrong. The system
works identically either way since every agent in this checkout has filesystem access
regardless of git tracking.

### 2026-07-29 — Consolidated tracking-file list instead of the requested flat structure

**Decision:** merged `CURRENT_CONTEXT.md`+`STATE.md` into one file, and `WORKLOG.md`+`TODO.md`
into `TASKS.md` + `sessions/`, rather than keeping all four as separate files.
**Reasoning:** more files answering overlapping questions means more places that can each say
something slightly different about "what's happening now," and in practice only the one an
agent happens to open gets updated. Fewer files with sharper single responsibilities stay
accurate longer. Full rationale: `.ai/README.md` § "Why this differs from the flat file list."
**Reversible:** yes, but not recommended without a concrete case where the merge caused a real
problem (not just "the original spec asked for four files").

### 2026-07-29 — `docs/` and `Plan.md` gitignored (project owner's decision, logged for context)

**Decision:** the full design documentation (`docs/`) and the original planning file (renamed
`Plan.md`) are excluded from git, staying local-only.
**Reasoning:** project owner doesn't want the deep design reasoning exposed to anyone who views
the repository externally. This is a standing constraint, not a one-off — see `RULES.md` #3 and
`PROJECT.md`'s hard-constraints list.
**Reversible:** the project owner's call, not an agent's, if it changes.

## Rules

- Newest entry at the top.
- Every entry states the decision, the reasoning, and whether it's reversible — skipping the
  reasoning defeats the purpose of the file (the decision alone is what `TASKS.md` already
  shows).
- Don't delete an old entry even if later superseded — add a new entry noting the supersession
  and link back to the one it replaces.
