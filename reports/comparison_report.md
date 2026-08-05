# Medical RAG Experiment Comparison Report

## Executive Summary & Production Recommendation

**Recommended Production Configuration**: `run_2_qdrant_linear`
- **Vector Store**: `qdrant`
- **Embedding Model**: `amazon.titan-embed-text-v2:0`
- **Orchestration**: `N/A`
- **NDCG@10**: `1.6309`
- **Faithfulness**: `0.4222`
- **Avg Latency**: `815.48 ms`

## Matrix Benchmark Comparison Table

| Run Name | Vector Store | Embedding | Orchestration | MRR@10 | NDCG@10 | Faithfulness | Latency (ms) |
|---|---|---|---|---|---|---|---|
| `run_2_qdrant_linear` | `qdrant` | `amazon.titan-embed-text-v2:0` | `N/A` | `1.0` | `1.6309` | `0.4222` | `815.48` |
| `run_1_qdrant_linear` | `qdrant` | `amazon.titan-embed-text-v2:0` | `N/A` | `1.0` | `1.6309` | `0.3231` | `6383.41` |
