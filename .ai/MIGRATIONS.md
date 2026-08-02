# Migrations log

> **Purpose:** a chronological record of every schema-changing event — vector-store schema
> changes, config-schema changes, dataset-version bumps — so an agent can tell whether an index
> or a cached artifact was built against the current schema or a stale one.
> **Who updates it:** whoever makes a schema-changing change.
> **When it's updated:** in the same session as the change, immediately, not batched later —
> a schema change without a same-session log entry is exactly what causes a future agent to
> debug a mismatch that was never recorded.
> **Read by:** any agent about to trust an existing index, dataset artifact, or config file
> without rebuilding it.

## What counts as a migration here

- A vector-store collection/class schema change (new payload field, changed vector dimension,
  changed distance metric) — existing collections built under the old schema become stale.
- A dataset processing change that alters the corpus or qrels shape — existing content hashes
  no longer match; downstream indexes built from the old hash are stale.
- A config schema change (`config/settings.example.yaml` / `experiment.example.yaml` shape) that
  isn't backward compatible — old config files won't load.
- An MLflow logged-params/metrics shape change that would make old runs incomparable to new ones
  in the same experiment.

**Not** a migration: adding an optional field with a safe default, a new config file that
doesn't replace an old one, anything additive that doesn't invalidate existing artifacts.

## Log

| ID | Date | What changed | Why | Invalidates | Migration action taken |
|---|---|---|---|---|---|
| — | — | *(none yet — no schemas have been implemented; M4 will produce the first entries)* | | | |

## Entry format

```
| MIG-001 | 2026-08-15 | Added `pub_year` as an indexed Qdrant payload field | needed for recency self-query retrieval | all collections built before this date | re-indexed all four existing collections; no data loss, additive on Weaviate side, required rebuild on Qdrant side since payload indexes are created at collection-creation time |
```

## Rules

- Number entries sequentially (`MIG-001`, `MIG-002`, ...), never reuse a number.
- "Invalidates" should name specific artifacts (collection names, dataset hashes) where
  possible, not just "old data" — vague invalidation notes are as bad as no note.
- If a migration requires a rebuild (re-indexing, re-embedding), say so explicitly in "Migration
  action taken" — don't leave the next agent to discover that the hard way.
