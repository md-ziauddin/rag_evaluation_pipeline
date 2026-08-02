# Checkpoint: M0 — scaffolding + design docs + AI-OS complete — 2026-07-29

**Trigger:** Milestone M0 (environment & scaffolding), M0.5 (design documentation), and M0.6
(this AI operating system) are all complete. This is the boundary before M1 (dataset pipeline)
implementation work begins — the last point at which the project is pure design + tooling, no
application code.

## Project state at this point

| Milestone | Status |
|---|---|
| M0 — Environment & scaffolding | Done |
| M0.5 — Design documentation | Done |
| M0.6 — AI operating system | Done |
| M1 — Dataset pipeline | Not started (READY — no blockers except the two prerequisite checks below) |
| M2–M9 | Not started |

## What existed

- Full repo scaffold: `src/rag_eval/` (12 subpackages, `.gitkeep` only — no implementation),
  `pyproject.toml`, `requirements/{base,dev}.txt`, `.env.example`, `docker-compose.yml`
  (Qdrant + Weaviate + MLflow functional, `api` service commented placeholder), `Makefile`,
  `.github/workflows/ci.yml`, `config/{settings,experiment}.example.yaml`.
- Full 19-section design documentation set under `docs/` (gitignored, present locally):
  product, architecture (+ 12 ADRs), retrieval, evaluation, planning, engineering, risks.
- Full `.ai/` operating system (this file's own directory): 18 root files, 4 templates,
  3 scripts, 2 session records.
- Root pointer files for cross-tool bootstrap: `CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
  `.cursorrules`, plus `.vscode/tasks.json`.
- **Zero lines of application code.** No chunkers, no providers, no adapters, no retrievers, no
  API routes exist yet — everything above is scaffolding, documentation, or tooling.

## What was verified working

- `docker compose config` parses the compose file without error.
- All internal markdown links across the 19-section design set resolve.
- YAML files (`docker-compose.yml`, `ci.yml`, both config examples) parse cleanly.
- `.env.example` covers every environment variable referenced by
  `docs/architecture/configuration-management.md`.
- `.ai/scripts/validate.py` runs clean against the `.ai/` system itself (after fixing a
  false-positive bug in its own path-resolution logic during this session).
- **Not yet verified:** `make up` has not been run against a live Docker daemon in this
  environment — `docker compose config` confirms the file is syntactically valid, not that the
  services actually start and pass health checks.
- **Not yet verified:** AWS Bedrock model access for the target account/region.

## Known issues / deferred work at this point

- The two M0→M1 prerequisite checks above (`make up`, Bedrock access) are the immediate next
  actions — see `STATE.md`.
- `MedQA`'s Hugging Face loader is known (from the design docs) to require
  `trust_remote_code=True` and to have no per-passage relevance labels — both are documented
  constraints (ADR 0012, `docs/planning/implementation-plan.md` Phase 1), not yet encountered in
  actual code since no loader has been written.
- `docs/` and `Plan.md` are gitignored by project owner request; a rollback to this checkpoint
  on a fresh clone would be missing both unless restored from a non-git backup.

## Git reference

**Commit:** `bf28552` covers the scaffold (M0). The design docs (M0.5) and this `.ai/` system
(M0.6) were not yet committed as of this checkpoint — see the suggested commit message in
`sessions/2026-07-29-1940-claude-code.md`.
