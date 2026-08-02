# Rules for every AI agent

> **Purpose:** hard constraints that apply regardless of which agent or tool is operating.
> **Who updates it:** the project owner. An agent may propose an addition via `DECISIONS.md`,
> but does not add to this file unilaterally.
> **When it's updated:** when a real failure shows a rule is missing, not speculatively.
> **Read by:** every agent, as part of `BOOTSTRAP.md`.

These are constraints, not suggestions. "I thought it would be fine" is not a defense for
skipping one.

## File safety

1. **Never create a file without checking `FILE_INDEX.md` first.** If it's already there and
   not deprecated, edit it.
2. **Never delete a file's `FILE_INDEX.md` row.** Mark it `deprecated`/`deleted` and say why.
   Rows are history, not clutter.
3. **Never silently rewrite a file another agent marked with a non-obvious reason in its
   `FILE_INDEX.md` notes.** If you disagree with a prior decision, record the disagreement in
   `DECISIONS.md` and get it resolved before overwriting.

## Architectural constraints

4. **Never contradict `ARCHITECTURE.md` without a new `DECISIONS.md` entry that supersedes it.**
   Swapping Qdrant for something else, or LangChain for a hand-rolled loop, is a decision, not a
   drive-by edit — it needs a record, the same as the original choice got one.
5. **Never introduce a new external dependency (service, paid API, new database) without
   flagging it in `DECISIONS.md` first**, even if you're confident it's the right call. Cost and
   credential implications are the project owner's to approve, not infer.

## Task and state discipline

6. **Never mark a task `DONE` in `TASKS.md` without also updating `FILE_INDEX.md` for every file
   that task touched.** A done task with stale file tracking is worse than an honest
   `IN_PROGRESS`.
7. **Never end a session without running `SHUTDOWN.md` in full**, even for small changes.
   A five-minute fix still needs its `FILE_INDEX.md`/`TASKS.md`/`CHANGELOG.md` rows updated and
   its session file written — that's how the next agent knows it happened at all.
8. **Never let `STATE.md` and `TASKS.md` disagree at the end of a session.** If they'd disagree,
   fix one before you stop, per `SHUTDOWN.md` step 8.

## Data and secrets

9. **Never commit a dataset, a built vector index, or anything under `data/`/`experiments/`.**
   Those are gitignored for a reason — they're large and non-reproducible-by-diff. Version them
   by content hash in `MIGRATIONS.md`/`DATABASE.md`, not by committing the file.
10. **Never put a credential, API key, or secret in any `.ai/` file, in `docs/`, or in code.**
    Secrets live in `.env` only, which is gitignored. If you need to reference that a secret
    exists, name the environment variable, not the value.
11. **Never send data to Bedrock (or any external model provider) that could be PHI without the
    project owner explicitly confirming a BAA is in place.** Public research datasets only,
    per `ARCHITECTURE.md`'s constraint list, unless that's explicitly revisited.

## Ambiguity

12. **When `BOOTSTRAP.md` step 9's conditions are met, stop and ask.** Don't pick the option
    that seems safer and proceed silently — an unasked question that turns out to matter is far
    more expensive than the ten seconds it costs to ask.
13. **Don't manufacture ambiguity to avoid a decision that's actually yours to make.** Routine
    implementation choices (a variable name, which of two equivalent approaches, a default
    value) are yours. Save "wait for confirmation" for things that are genuinely hard to undo.

## Style and scope

14. **Match the existing code and doc style** (`docs/engineering/documentation-plan.md` if
    present covers doc conventions; `pyproject.toml`'s `[tool.ruff]`/`[tool.mypy]` covers code).
15. **Don't refactor, rename, or "clean up" code you weren't asked to touch**, even if you
    notice something you'd do differently. Flag it in `DECISIONS.md` or as a `TASKS.md` backlog
    entry instead of doing it as a drive-by inside an unrelated task.
16. **Don't add a dependency, config option, or abstraction "for future flexibility."** Build
    what the current task needs. `docs/risks/future-roadmap.md`, if present, is where deferred
    scope goes.

## Enforcement

None of this is enforced by a tool today — see `README.md`'s "Future improvements" for the CI
check that's planned. Until then, it's enforced by every agent actually reading this file during
`BOOTSTRAP.md` and by the project owner spot-checking `git log` against `SESSION_LOG.md`.
