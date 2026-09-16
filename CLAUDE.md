# Claude Code — Project Instructions

Production Medical Retrieval-Augmented Generation (RAG) Architecture and Evaluation System.

## Architecture & Code Structure
- Core package: `src/rag_eval/`
- Orchestration: Linear RAG pipeline (`rag_eval.orchestration.linear`) and LangGraph Agentic graph (`rag_eval.orchestration.agentic`)
- LLM Generation: Prioritized fallback Bedrock > Groq via `LLMFactory` (`rag_eval.generation.factory`)
- Vector Stores: Qdrant (`rag_eval.vector_stores.qdrant_store`) and Weaviate (`rag_eval.vector_stores.weaviate_store`)
- Evaluation: 3-layer metrics with IR, Generation, and Systems metrics tracked in MLflow
- REST Service: FastAPI application at `rag_eval.api.main:app`

## Quality Gates & Verification
Always verify all changes against the project quality gates before committing:

```bash
# 1. Formatting and linting
ruff check .
ruff format --check .

# 2. Static type checking
mypy src/

# 3. Security audit
bandit -r src/

# 4. Automated tests (unit + integration via testcontainers)
pytest -v
```

Or run all verification gates with:
```bash
./scripts/check.sh
```

## Infrastructure
Start microservices (Qdrant, Weaviate, MLflow, API):
```bash
docker compose up -d
```
