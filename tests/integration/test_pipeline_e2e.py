"""
End-to-End Integration Test Suite for Medical RAG Pipeline.

Verifies end-to-end integration across Ingestion, Chunking, Embeddings, Vector Store Indexing,
Retrieval, Dual Orchestration, Metrics Calculation, and MLflow Logging against a real Dockerized
Qdrant instance via testcontainers.
"""

import time
import urllib.request
from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from testcontainers.core.container import DockerContainer

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.evaluation.evaluator import RAGEvaluator
from rag_eval.orchestration.agentic import AgenticRAGGraph
from rag_eval.orchestration.linear import LinearRAGPipeline
from rag_eval.retrieval.bm25 import BM25Retriever
from rag_eval.retrieval.dense import DenseRetriever
from rag_eval.retrieval.ensemble import EnsembleRetriever
from rag_eval.vector_stores.qdrant_store import QdrantVectorStore


@pytest.fixture(scope="module")
def qdrant_container() -> Generator[str, None, None]:
    """Spins up a real Qdrant container via testcontainers for integration tests."""
    container = DockerContainer("qdrant/qdrant:v1.12.4").with_exposed_ports(6333)
    with container:
        port = container.get_exposed_port(6333)
        host = container.get_container_host_ip()
        url = f"http://{host}:{port}"
        # Wait until Qdrant is fully ready to accept connections
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"{url}/readyz", timeout=1) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                time.sleep(0.2)
        yield url


@pytest.mark.integration
class TestE2EPipelineIntegration:
    """Integration test suite executing pipelines against real Dockerized Qdrant."""

    @patch("rag_eval.evaluation.tracker.MLflowTracker")
    def test_e2e_linear_pipeline_flow(
        self,
        mock_tracker_class: MagicMock,
        qdrant_container: str,
        mock_embedding_provider: Any,
        mock_llm_provider: Any,
    ) -> None:
        # 1. Setup MLflow Tracker Mock
        mock_tracker = MagicMock()
        mock_run = MagicMock()
        mock_run.info.run_id = "e2e-run-linear-001"
        mock_tracker.start_run.return_value.__enter__.return_value = mock_run
        mock_tracker.log_evaluation_run.return_value = "e2e-run-linear-001"
        mock_tracker_class.return_value = mock_tracker

        # 2. Ingestion & Chunking
        chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
        doc = ChunkDocument(
            doc_id="doc1",
            content=(
                "Mitochondria undergo structural changes during morphogenesis and cell death."
            ),
            source="pubmed",
            metadata={},
        )
        chunks = chunker.chunk(doc)
        assert len(chunks) > 0

        # 3. Embeddings & Real Vector Store Indexing (Dockerized Qdrant)
        embed_provider = mock_embedding_provider
        vstore = QdrantVectorStore(
            collection_name="e2e_linear_test_col",
            dimension=embed_provider.dimension,
            url=qdrant_container,
        )
        vstore.create_collection(force_recreate=True)

        chunk_texts = [c.text for c in chunks]
        vectors = embed_provider.embed_documents(chunk_texts)
        vstore.index_chunks(chunks, vectors)

        # 4. Retrieval & Ensemble (Dense + BM25)
        dense_ret = DenseRetriever(embed_provider=embed_provider, vector_store=vstore)
        bm25_ret = BM25Retriever(chunks=chunks)
        retriever = EnsembleRetriever(retrievers=[dense_ret, bm25_ret], rrf_k=60)

        # 5. Orchestration & LLM Generation
        llm = mock_llm_provider
        pipeline = LinearRAGPipeline(retriever=retriever, llm_provider=llm)

        res = pipeline.run("What role do mitochondria play?")
        assert "Mitochondria" in res["answer"]
        assert len(res["retrieved_chunks"]) > 0
        assert res["pipeline_type"] == "linear"

        # 6. Evaluation & MLflow Logging
        evaluator = RAGEvaluator(tracker=mock_tracker)
        test_cases = [{"query": "What role do mitochondria play?", "doc_id": "doc1"}]

        eval_res = evaluator.evaluate_pipeline(
            pipeline=pipeline,
            test_cases=test_cases,
            run_name="e2e_linear_test",
            pipeline_params={"pipeline_type": "linear"},
        )
        assert eval_res["run_id"] == "e2e-run-linear-001"
        assert "ndcg_at_10" in eval_res["metrics"]
        assert eval_res["metrics"]["mrr_at_10"] > 0.0

    @patch("rag_eval.evaluation.tracker.MLflowTracker")
    def test_e2e_agentic_pipeline_flow(
        self,
        mock_tracker_class: MagicMock,
        qdrant_container: str,
        mock_embedding_provider: Any,
        mock_llm_provider: Any,
    ) -> None:
        # 1. Setup MLflow Tracker Mock
        mock_tracker = MagicMock()
        mock_run = MagicMock()
        mock_run.info.run_id = "e2e-run-agentic-002"
        mock_tracker.start_run.return_value.__enter__.return_value = mock_run
        mock_tracker_class.return_value = mock_tracker

        # 2. Ingestion & Chunking
        chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
        doc = ChunkDocument(
            doc_id="doc1",
            content="Mitochondrial permeability transition pore initiates programmed cell death.",
            source="pubmed",
            metadata={},
        )
        chunks = chunker.chunk(doc)

        # 3. Real Vector Store Indexing (Dockerized Qdrant)
        embed_provider = mock_embedding_provider
        vstore = QdrantVectorStore(
            collection_name="e2e_agentic_test_col",
            dimension=embed_provider.dimension,
            url=qdrant_container,
        )
        vstore.create_collection(force_recreate=True)

        chunk_texts = [c.text for c in chunks]
        vectors = embed_provider.embed_documents(chunk_texts)
        vstore.index_chunks(chunks, vectors)

        # 4. Retrieval & Agentic Orchestration
        dense_ret = DenseRetriever(embed_provider=embed_provider, vector_store=vstore)
        bm25_ret = BM25Retriever(chunks=chunks)
        retriever = EnsembleRetriever(retrievers=[dense_ret, bm25_ret], rrf_k=60)
        llm = mock_llm_provider

        agentic_graph = AgenticRAGGraph(retriever=retriever, llm_provider=llm)
        res = agentic_graph.run("How do mitochondria initiate cell death?")

        assert "answer" in res
        assert len(res["retrieved_chunks"]) > 0
        assert res["pipeline_type"] == "agentic"
