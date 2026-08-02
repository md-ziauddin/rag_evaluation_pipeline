# Prompt memory

> **Purpose:** a record of the prompts that generated major, non-trivial project artifacts —
> so nobody regenerates a feature or a design doc that already exists because they didn't know
> a prior prompt already produced it.
> **Who updates it:** whichever agent executes a prompt that produces a major artifact (a design
> doc set, a generated module, a substantial refactor).
> **When it's updated:** immediately after the artifact is produced, in the same session.
> **Read by:** any agent about to start work that sounds like "write the design docs" or
> "build the AI-OS" or similarly broad — check here first.

**Register here:** prompts that produced a design doc set, a whole module, a generated schema,
or anything expensive to regenerate. **Don't register:** routine "fix this bug" or "add this
field" prompts — those belong in the relevant `sessions/` file, not here.

## Log (most recent first)

### PROMPT-002 — AI operating system design

**Date:** 2026-07-29 · **Agent:** Claude Code · **Produced:** `.ai/` in full (18 files +
templates + scripts + root pointer files `CLAUDE.md`/`AGENTS.md`/`GEMINI.md`/`.cursorrules` +
`.vscode/tasks.json`).

**Prompt summary:** requested a repository-level "AI Operating System" so multiple non-memory-
sharing AI agents (Claude Code, Gemini CLI, Codex, Cursor) can hand off work without duplicating
it — covering task tracking, file indexing, architectural decisions, API/DB/migration tracking,
prompt memory, session logs, a bootstrap procedure, and a shutdown procedure. Explicitly
requested as a redesignable structure ("improve this significantly"), not a fixed template.

**Do not re-run this prompt** to "regenerate the AI-OS" — it exists. If it needs to change,
edit the specific file; see `RULES.md` for who's allowed to edit what.

### PROMPT-001 — Full design documentation set + repo scaffolding

**Date:** 2026-07-29 · **Agent:** Claude Code · **Produced:** `docs/` (19-section design set:
executive summary, PRD, system architecture, 12 ADRs, folder structure, configuration
management, retrieval/chunking/embedding design, evaluation framework, experiment tracking,
roadmap, task breakdown, implementation plan, testing strategy, CI/CD, documentation plan,
risks, future roadmap) + the full repo scaffold (`src/rag_eval/` package skeleton,
`pyproject.toml`, `docker-compose.yml`, CI workflow, config examples, `.env.example`).

**Prompt summary:** requested staff-engineer-level design documentation for a production-grade
medical RAG evaluation pipeline comparing retrieval strategies, vector databases, and search
techniques, written to the standard a second team could build from — explicitly "no
implementation code" in that pass. Provider: AWS Bedrock default with open-source models
benchmarked as alternatives. Docs grouped by theme under `docs/`. Both docs and scaffolding
requested as deliverables.

**Do not re-run this prompt** to "regenerate the docs" — the full set exists in `docs/` (local,
gitignored). If a specific doc needs updating, edit that file directly and log the change in
`DECISIONS.md`/`CHANGELOG.md` as appropriate, don't regenerate the whole set.

## Rules

- Number sequentially, never reuse.
- Include enough of the original prompt's *intent* that a future agent can tell whether a new
  request is "the same thing again" or genuinely different scope — a one-line summary isn't
  enough if two different prompts could produce a similar-sounding artifact.
- Link the artifact's location, not just its name — "the docs" isn't findable, `docs/` is.
