# Database and schema registry

> **Purpose:** every schema this project defines — vector-store collections/classes, the
> experiment-tracking store, and any config schema treated as a contract. There's no
> traditional relational database here; "database" covers what actually needs schema
> discipline in this project.
> **Who updates it:** whoever creates or changes a collection/class definition or a tracked
> config schema.
> **When it's updated:** in the same session as the schema change, alongside a `MIGRATIONS.md`
> entry if the change is breaking.
> **Read by:** any agent touching `src/rag_eval/vectorstores/`, `ingestion/`, or `config/`.

## Status: not yet implemented

No collections/classes have been created (milestone M4). The schemas below are the **planned**
shape, sourced from `docs/architecture/configuration-management.md` and
`docs/retrieval/chunking-strategy.md` — implement against these rather than redesigning them.

## Qdrant collection (planned)

| Field | Type | Notes |
|---|---|---|
| Dense vector | float32[dim] | dim depends on embedding model (see `docs/retrieval/embedding-strategy.md`) |
| Sparse vector | sparse | BM25/BM42 or SPLADE representation, for native hybrid |
| Payload: `doc_id` | keyword, indexed | provenance, maps back to qrels |
| Payload: `chunk_id` | keyword | chunk identity |
| Payload: `parent_id` | keyword, nullable | parent-document retrieval linkage |
| Payload: `source` | keyword, indexed | `pubmedqa` \| `medqa` |
| Payload: `section` | keyword, indexed | e.g. background/methods/results; medical-section-aware chunking |
| Payload: `pub_year` | integer, indexed | recency filtering, self-query |
| Payload: `mesh_terms` | keyword[], indexed | domain filtering (PubMedQA `meshes`) |

One collection per (embedding model × chunking strategy) combination under test — naming
convention to be fixed when M4 starts; record it here and in `MIGRATIONS.md` once decided.

## Weaviate class (planned)

Same logical fields as the Qdrant payload above, as class properties, with
`DEFAULT_VECTORIZER_MODULE=none` (vectors supplied externally — see `ARCHITECTURE.md`). Property
indexing configured on the same filterable fields (`section`, `pub_year`, `mesh_terms`).

## Chunk metadata schema (shared contract, both stores)

Defined once and used identically by both adapters, per
`docs/retrieval/chunking-strategy.md` § Chunk metadata schema: `doc_id`, `chunk_id`,
`parent_id`, `source`, `section`, `pub_year`, `mesh_terms`, `char_span`/`token_span`. Do not let
the Qdrant and Weaviate adapters drift on field names — a filter that works on one and silently
no-ops on the other is exactly the kind of bug this registry exists to prevent.

## MLflow (tracking store)

SQLite backend, local artifact root, both inside the `mlflow` compose service's gitignored
volume (`volumes/mlflow/`). Schema is MLflow's own (params/metrics/artifacts/tags per run) — not
something this project defines. What this project logs into it (which params, which metrics) is
specified in `docs/evaluation/experiment-tracking.md`.

## Dataset versioning (not a "database" but tracked here)

Processed dataset outputs (corpus, PubMedQA qrels, MedQA MCQ set) are content-hashed, not
committed. The manifest format (source, counts, hash, license) is defined in
`docs/planning/task-breakdown.md` T1.3 — implement against that spec.

## History

See `MIGRATIONS.md` for every schema-changing event once implementation begins.
