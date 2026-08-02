# Bootstrap procedure

> **Purpose:** the exact steps an agent runs before writing any code, so every agent starts
> from the same understanding regardless of which tool it is.
> **Who updates it:** the project owner, rarely. Agents follow it; they don't edit it mid-run.
> **When it's updated:** when the procedure itself needs to change (a new tracking file is
> added, a step turns out to be missing).
> **Read by:** every agent, at the start of every session, before any file write.

Run every step below, in order. Don't skip a step because the task "seems simple" — the whole
point of this procedure is that you don't get to judge that until you've done step 1–7.

## Step 1 — Read the fixed files

Open these, in this order:

1. `.ai/PROJECT.md` — what this is, stack, hard constraints, non-goals.
2. `.ai/STATE.md` — current milestone, current phase, what's blocked.
3. `.ai/TASKS.md` — filter to `IN_PROGRESS` and `BLOCKED`. This is the live edge of the project.
4. `.ai/ARCHITECTURE.md` — the locked-in technical decisions. Do not propose alternatives to
   anything on this list without first checking whether it's already an ADR with recorded
   alternatives-considered (it almost certainly is).

## Step 2 — Build project understanding

From steps above, you should now be able to state, without looking anything up again:

- What the project is and what it explicitly is not (non-goals).
- Which milestone (M0–M9, per `docs/planning/roadmap.md` if present, else `STATE.md`'s summary)
  the project is currently in.
- Which vector databases, embedding provider, orchestration framework, and tracking tool are
  fixed, and why (one-line reasons live in `ARCHITECTURE.md`; full reasoning is in
  `docs/architecture/adr/` if that directory exists in this checkout).

## Step 3 — Detect current milestone and unfinished work

Cross-reference `STATE.md`'s milestone against `TASKS.md`. If they disagree (e.g. `STATE.md`
says M3 but every M3 task in `TASKS.md` is still `BACKLOG`), stop and flag the mismatch instead
of picking one silently — this means the last session's shutdown was incomplete.

## Step 4 — Detect existing files

Before creating **any** file:

```
grep -i "<filename or close variant>" .ai/FILE_INDEX.md
```

If it's listed and not marked `Deprecated`, that file already exists — open and edit it. If it's
marked `Deprecated`, read its `Replace?` column before touching anything nearby. If it's not
listed at all, do a real filesystem check too (`FILE_INDEX.md` only tracks files someone
bothered to register — it is not guaranteed exhaustive for very recent, unregistered work).

## Step 5 — Detect architectural constraints

Read the constraint list in `ARCHITECTURE.md` fully, not just the ADR titles. A constraint
without its one-line reason is a rule you'll be tempted to break the first time it's
inconvenient.

## Step 6 — Refuse to recreate completed work

If the task you've been given describes something `TASKS.md` already marks `DONE`, or something
`FILE_INDEX.md` shows already exists and is not deprecated: **stop, say so, and ask what's
actually wanted** (a fix? an extension? was the requester unaware it exists?). Do not silently
rebuild it "to be safe" — that's the exact failure this system exists to prevent.

## Step 7 — Summarize understanding before coding

State back, in a few sentences, not a wall of text:

- What you understand the task to be.
- What already exists that's relevant (file paths, from `FILE_INDEX.md`).
- Which milestone/task this falls under (a `TASKS.md` ID, or "new — not yet tracked").
- Any constraint from `ARCHITECTURE.md` that bears on this task.

## Step 8 — Produce an execution plan

A short, concrete plan: files you'll touch (new vs. edit), in what order, and what "done" looks
like for this task. If the task is small, this can be two lines. It does not need to be a
formal planning-tool artifact — it needs to exist so the summary in step 7 isn't the only trace
of your reasoning before you start editing.

## Step 9 — Wait for confirmation if ambiguity exists

If any of the following is true, stop and ask before writing code:

- `STATE.md` and `TASKS.md` disagree on current milestone (step 3).
- The requested work overlaps a file marked `DONE`/existing without a clear instruction to
  modify vs. rebuild it (step 6).
- The task requires a decision that isn't covered by anything in `ARCHITECTURE.md` or
  `DECISIONS.md`, and picking wrong would be expensive to undo (new dependency, new external
  service, a schema change — see `MIGRATIONS.md` for what counts as schema-changing).
- Two tracking files contradict each other in a way you can't resolve by reading a third.

If none of these hold, proceed — don't manufacture ambiguity to avoid making a call.

## What "done" with bootstrap looks like

You've read four files, you've stated your understanding back, you have a plan, and you either
started working or asked one specific question. If you did none of that and just started
editing files, you skipped bootstrap — go back to step 1.
