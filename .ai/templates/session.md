<!--
Template for .ai/sessions/YYYY-MM-DD-HHMM-<agent-name>.md
Copy this file, fill in every section, delete this comment block.
Created by scripts/new_session.sh at session start; filled in at SHUTDOWN.md step 7.
-->

# Session: YYYY-MM-DD HH:MM — <agent name>

**Agent:** <Claude Code | Gemini CLI | Codex | Cursor | ...>
**Objective:** <one or two sentences — what was this session for>
**Milestone/tasks:** <TASKS.md IDs touched, e.g. T1.1, T1.2>

## Files touched

| File | Change | Why |
|---|---|---|
| `path/to/file` | created / edited / deleted | one clause |

## Reasoning

<Anything non-obvious: why this approach over an alternative, a tradeoff made, a constraint
that shaped the implementation. Skip this section only if the work was truly mechanical.>

## Completed

- <what got finished, matching TASKS.md rows moved to DONE/IN_REVIEW>

## Left for next session

- <what's unfinished, and specifically what "finish it" means>

## Warnings for whoever picks this up

- <anything that will bite the next agent if they don't know it — a gotcha, a workaround,
  a thing that looked like a bug but wasn't>

## Tracking files updated this session

- [ ] TASKS.md
- [ ] FILE_INDEX.md
- [ ] STATE.md
- [ ] CHANGELOG.md
- [ ] SESSION_LOG.md
- [ ] DECISIONS.md (if applicable)
- [ ] API.md / DATABASE.md / MIGRATIONS.md (if applicable)

## Suggested commit message

```
<type>: <summary>

<body>

AI-Session: sessions/YYYY-MM-DD-HHMM-<agent-name>.md
```
