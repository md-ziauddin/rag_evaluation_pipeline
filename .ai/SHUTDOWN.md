# Shutdown procedure

> **Purpose:** the exact steps an agent runs before ending a session, so the next agent (in any
> tool) never inherits a stale or contradictory picture of the project.
> **Who updates it:** the project owner, rarely.
> **When it's updated:** when a new tracking file is added that shutdown needs to touch.
> **Read by:** every agent, at the end of every session, before the session ends.

Run every step below. If the session made zero file changes (pure Q&A, no edits), skip straight
to step 8 — there's nothing to reconcile, but the session still gets a log entry so its
reasoning isn't lost.

## Step 1 — Update completed tasks

For every task you finished this session, move it to `DONE` in `TASKS.md` (see that file's state
machine). Add the completion date and, if relevant, a one-line note on what changed from the
original plan.

## Step 2 — Update file tracking

In `FILE_INDEX.md`:

- Add a row for every file you **created**.
- Update the "Last modified" and "Dependencies"/"Consumers" columns for every file you **edited**
  in a way that changed its shape (new function others will call, changed schema, new import).
  A whitespace or comment-only edit doesn't need a row update.
- Mark `Deprecated: yes` and fill in `Replace?` for every file you made obsolete. **Do not
  delete the row** — deprecated history is exactly what stops the next agent from recreating a
  thing that was deliberately replaced.
- For every file you **deleted**, keep its row, set `Status: deleted`, and note why in the
  nearest relevant `DECISIONS.md` entry.

## Step 3 — Update architecture and API/DB tracking, if touched

- If you made or changed a technical decision that constrains future work, add it to
  `DECISIONS.md` (see that file for the bar between a quick decision and a full ADR).
- If you added, removed, or changed an API endpoint, update `API.md`.
- If you changed a vector-store schema, a config schema, or anything else `DATABASE.md` tracks,
  update `DATABASE.md` **and** add an entry to `MIGRATIONS.md` — schema changes are exactly what
  silently breaks the next agent's assumptions if unrecorded.

## Step 4 — Record blockers and next actions

In `STATE.md`, update:

- Current milestone/phase, if it moved.
- The "Blocked on" line — what's stopping the next session, specifically (a missing credential,
  a decision the project owner needs to make, a failing test you didn't have time to fix).
- The "Next actions" line — the two or three things that should happen next, in priority order.

## Step 5 — Record the git commit suggestion

Propose (don't execute unless asked) a commit message covering this session's changes, in the
repo's existing style (see prior commits and `docs/engineering/cicd.md` if present). Include the
`AI-Session:` trailer pointing at the session file you're about to write in step 7:

```
AI-Session: sessions/<this-session-file>.md
```

## Step 6 — Update the changelog

Add an entry to `CHANGELOG.md` under `Unreleased`, in Keep-a-Changelog style
(`Added`/`Changed`/`Fixed`/`Removed`), one line per user-visible or agent-visible change. Skip
purely internal refactors that don't change behavior or interface.

## Step 7 — Write the session file

Create `.ai/sessions/YYYY-MM-DD-HHMM-<agent-name>.md` from `templates/session.md` (or run
`scripts/new_session.sh <agent-name>` at the *start* of the session and fill it in now). Include:
agent, objective, files touched, reasoning for non-obvious choices, what got completed, what's
left, and any warnings for whoever picks this up next.

Then add one row to `SESSION_LOG.md` pointing at that file.

## Step 8 — Final consistency check

Before ending the session, confirm:

- `STATE.md`'s milestone matches the aggregate state of `TASKS.md` (no session should end with
  `STATE.md` claiming a milestone that `TASKS.md` shows as still mostly `BACKLOG`).
- Every file you created this session has a `FILE_INDEX.md` row.
- The session file exists and `SESSION_LOG.md` references it.

If any of those is false, fix it now — a shutdown that skips this step is the single most common
way this system rots.

## What "done" with shutdown looks like

`TASKS.md`, `FILE_INDEX.md`, `STATE.md`, `CHANGELOG.md`, and `SESSION_LOG.md` all reflect this
session's work, a new file exists under `sessions/`, and a commit message is ready. That's a
clean handoff — the next agent, in any tool, can run `BOOTSTRAP.md` and pick up exactly where
you left off.
