# Medical RAG Experiment Comparison Report

## Executive Summary & Production Recommendation

**Recommended Production Configuration**: `run_1_qdrant_dense_linear`
- **Vector Store**: `qdrant`
- **Embedding Model**: `amazon.titan-embed-text-v2:0`
- **Retrieval Strategy**: `dense`
- **Orchestration**: `linear`
- **NDCG@10**: `0.9471`
- **Faithfulness**: `0.3732`
- **Avg Latency**: `7550.61 ms`

## Matrix Benchmark Comparison Table

| Run Name | Vector Store | Embedding | Retrieval | Orchestration | MRR@10 | NDCG@10 | Faithfulness | Latency (ms) |
|---|---|---|---|---|---|---|---|---|
| `run_1_qdrant_dense_linear` | `qdrant` | `amazon.titan-embed-text-v2:0` | `dense` | `linear` | `0.445` | `0.9471` | `0.3732` | `7550.61` |
| `run_2_qdrant_dense_agentic` | `qdrant` | `amazon.titan-embed-text-v2:0` | `dense` | `agentic` | `0.445` | `0.9471` | `0.3684` | `7568.71` |
| `run_4_qdrant_hybrid_agentic` | `qdrant` | `amazon.titan-embed-text-v2:0` | `hybrid` | `agentic` | `0.2922` | `0.6441` | `0.3629` | `7391.81` |
| `run_3_qdrant_hybrid_linear` | `qdrant` | `amazon.titan-embed-text-v2:0` | `hybrid` | `linear` | `0.2583` | `0.5587` | `0.3436` | `7188.31` |
