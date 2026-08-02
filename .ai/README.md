# .ai/ — the project's operating system

This directory is the shared memory for every AI agent that touches this repository. Claude
Code, Gemini CLI, Codex, Cursor, and whatever comes next do not share state with each other —
each starts cold. `.ai/` is how a cold agent gets warm in under two minutes instead of
re-reading the whole codebase and re-deriving decisions that were already made.

The rule that makes this work: **one file, one job, one owner.** Every file below answers a
different question. If two files could answer the same question, one of them will drift and
lie. That's why this design consolidates several of the "obvious" files (CURRENT_CONTEXT,
WORKLOG, TODO, SESSION_LOG-as-content) into fewer files with sharper responsibilities — see
"Why this differs from a flat file list" at the bottom.

## Read this first if you're an agent

Don't read this whole system. Read **[BOOTSTRAP.md](BOOTSTRAP.md)** — it's the procedure, and
it tells you exactly which files to open and in what order. This README is for humans and for
agents that want the map before the procedure.

## The files, one line each

| File | Answers |
|---|---|
| [BOOTSTRAP.md](BOOTSTRAP.md) | "What do I do before writing any code?" |
| [SHUTDOWN.md](SHUTDOWN.md) | "What do I do before ending this session?" |
| [RULES.md](RULES.md) | "What am I never allowed to do?" |
| [PROJECT.md](PROJECT.md) | "What is this project, in 30 seconds?" |
| [STATE.md](STATE.md) | "Where are we right now?" (the single most important file) |
| [TASKS.md](TASKS.md) | "What's done, in progress, blocked, or next?" |
| [FILE_INDEX.md](FILE_INDEX.md) | "Does this file already exist? Can I edit it?" |
| [ARCHITECTURE.md](ARCHITECTURE.md) | "What technical decisions are already locked in?" |
| [API.md](API.md) | "What endpoints exist or are planned?" |
| [DATABASE.md](DATABASE.md) | "What's the schema — vector collections, tracking store?" |
| [MIGRATIONS.md](MIGRATIONS.md) | "What schema-changing events have happened?" |
| [DECISIONS.md](DECISIONS.md) | "What did we decide recently, and why?" (fast log, not full ADRs) |
| [CHANGELOG.md](CHANGELOG.md) | "What changed, release by release?" |
| [PROMPTS.md](PROMPTS.md) | "What prompt already built this feature?" |
| [SESSION_LOG.md](SESSION_LOG.md) | "What sessions have happened?" (index, one row each) |
| [WORKFLOW.md](WORKFLOW.md) | "Show me a worked example of the whole system." |
| `sessions/` | Full record of each individual session |
| `checkpoints/` | Heavier state snapshots taken at milestone boundaries |
| `templates/` | Stubs used to create new sessions/tasks/decisions/checkpoints |
| `scripts/` | Automation: new-session scaffolding, index validation |

Every file in this list carries its own header block (Purpose / Owner / Updated by / When) at
the top, so you never have to come back here to know who's responsible for it.

## Two-minute onboarding, concretely

1. Open [STATE.md](STATE.md). One paragraph, tells you the current milestone and phase.
2. Open [TASKS.md](TASKS.md), filter to `IN_PROGRESS` and `BLOCKED`. That's the live edge.
3. Grep [FILE_INDEX.md](FILE_INDEX.md) for anything you're about to create. If it's there and
   not marked deprecated, edit it — don't recreate it.
4. Skim [ARCHITECTURE.md](ARCHITECTURE.md)'s constraint list once. Those are not up for
   re-litigation without a new entry in [DECISIONS.md](DECISIONS.md).
5. Start working. Follow [BOOTSTRAP.md](BOOTSTRAP.md) if you want the full checklist instead
   of the shortcut above.

That's it. If step 1–4 leaves you uncertain about scope, that's what "wait for confirmation" in
[BOOTSTRAP.md](BOOTSTRAP.md) is for — ask, don't guess.

## Where the deep design docs live

The full design set (executive summary, PRD, 12 ADRs, retrieval/chunking/embedding design,
evaluation methodology, roadmap) lives in `docs/` at the repo root. **`docs/` and `Plan.md` are
gitignored on purpose** — they hold the reasoning-heavy material the project owner doesn't want
exposed to external viewers of the repository. They still exist on disk in this checkout, and
every agent working here has filesystem access to them, so `.ai/ARCHITECTURE.md` and
`.ai/PROJECT.md` point into `docs/` rather than duplicating it. If you ever work from a fresh
clone that lacks `docs/`, say so — the `.ai/` files still carry enough of a constraint summary
to keep you from making a contradicting decision, but the full rationale won't be there.

**Whether `.ai/` itself should be committed or also gitignored is the project owner's call, not
mine.** I've treated `.ai/` as operational tracking (what exists, what's in progress, what's
locked in) rather than design rationale, and left it tracked by git by default. If you'd rather
keep it private too, gitignore `.ai/` the same way `docs/` is — the system works identically
either way since every agent here has local filesystem access regardless of what git tracks.

## Example workflow

See [WORKFLOW.md](WORKFLOW.md) for a full worked example: one agent finishes a task and hands
off to a different agent in a different tool, with no human re-explaining anything.

## Git integration

- Commit `.ai/STATE.md`, `TASKS.md`, `FILE_INDEX.md`, `DECISIONS.md`, `CHANGELOG.md`, and the
  new session/checkpoint file **in the same commit** as the code change they describe. A
  tracking file that lags the code it describes is worse than no tracking file.
- Suggested commit trailer so `git log` and `.ai/SESSION_LOG.md` cross-reference each other:
  ```
  AI-Session: sessions/2026-08-02-1430-claude-code.md
  ```
- A pre-commit hook can run `python .ai/scripts/validate.py` to catch `FILE_INDEX.md` drift
  before it lands (see `scripts/` and the automation section in [RULES.md](RULES.md)).

## VS Code integration

`.vscode/tasks.json` (repo root) adds three tasks: **AI: Show State** (cats `STATE.md` +
`TASKS.md`), **AI: New Session** (runs `scripts/new_session.sh <agent-name>`), and
**AI: Validate Index** (runs `scripts/validate.py`). Bind them to keyboard shortcuts if you
start/end sessions often.

## Future improvements

- A `scripts/validate.py` check that fails CI if a merged PR didn't touch `FILE_INDEX.md` for
  files it created (currently advisory, not enforced).
- Promote `DECISIONS.md` entries to formal ADRs automatically once an entry survives three
  sessions without being reversed — right now that promotion is manual.
- A machine-readable mirror of `STATE.md`/`TASKS.md` (e.g. `state.json`) if a script ever needs
  to parse rather than read them; deferred until something other than an LLM needs to consume
  them.
- Session files are markdown today because every target agent reads markdown natively with no
  parsing step; revisit only if the file count under `sessions/` becomes a real navigation
  problem (it hasn't at project scale).

## Why this differs from the flat file list you'd expect

A system with `CURRENT_CONTEXT.md`, `STATE.md`, `WORKLOG.md`, and `TODO.md` as four separate
files has four places that can each say something slightly different about "what's happening
right now," and in practice only the one an agent happens to open gets updated. This design
merges them:

- **`CURRENT_CONTEXT.md` + `STATE.md` → `STATE.md`.** One file for "where are we right now."
- **`WORKLOG.md` + `TODO.md` → `TASKS.md`** (with a task-level state machine) **+ `sessions/`**
  (with the play-by-play). The board tells you *what*; the session files tell you *how it went*.
- **`SESSIONS/` (raw name) → `sessions/`, `CHECKPOINTS/` → `checkpoints/`** — lowercase to match
  the rest of the repo's directory conventions.

Everything the original list asked to track still has a home; there are just fewer places an
agent could update one and forget the other.
