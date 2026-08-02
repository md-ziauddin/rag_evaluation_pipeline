<!--
Template for a new row in .ai/TASKS.md's "Active tasks" table.
Not a standalone file — paste this as a new table row when picking up untracked work.
-->

| ID | Task | Status | Owner | Blocked on |
|---|---|---|---|---|
| <EPIC-N or new ID> | <one-line description, specific enough that DONE is unambiguous> | BACKLOG | — | — |

Fill in as work progresses:
- **Status** moves through `BACKLOG → READY → IN_PROGRESS → IN_REVIEW → DONE`
  (side states: `BLOCKED`, `ABANDONED`, `SUPERSEDED` — see `STATE.md`'s task state machine).
- **Owner** — which agent/session is actively on it (blank if unclaimed).
- **Blocked on** — name the specific blocker (a decision, a credential, a failing test), not
  "stuff."

When it reaches `DONE`, move the row to `TASKS.md`'s "Completed" table with a completion date
and a link to the session file that finished it.
