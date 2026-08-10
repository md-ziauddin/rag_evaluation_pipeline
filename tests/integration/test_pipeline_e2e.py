"""
End-to-End Integration Test Suite for Medical RAG Pipeline.

Verifies end-to-end integration across Ingestion, Chunking, Embeddings, Vector Store Indexing,
Retrieval, Dual Orchestration, Metrics Calculation, and MLflow Logging.
"""

from unittest.mock import MagicMock, patch

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.evaluation.evaluator import RAGEvaluator
from rag_eval.generation.groq_provider import GroqLLMProvider
from rag_eval.orchestration.agentic import AgenticRAGGraph
from rag_eval.orchestration.linear import LinearRAGPipeline
from rag_eval.retrieval.bm25 import BM25Retriever
from rag_eval.retrieval.dense import DenseRetriever
from rag_eval.retrieval.ensemble import EnsembleRetriever
from rag_eval.vector_stores.factory import VectorStoreFactory


class TestE2EPipelineIntegration:
    """Integration test suite for the complete pipeline execution flow."""

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    @patch("rag_eval.generation.groq_provider.Groq")
    @patch("rag_eval.evaluation.tracker.MLflowTracker")
    def test_e2e_linear_pipeline_flow(self, mock_tracker_class, mock_groq_class, mock_qdrant_class):
        # 1. Setup MLflow Tracker Mock
        mock_tracker = MagicMock()
        mock_run = MagicMock()
        mock_run.info.run_id = "e2e-run-linear-001"
        mock_tracker.start_run.return_value.__enter__.return_value = mock_run
        mock_tracker.log_evaluation_run.return_value = "e2e-run-linear-001"
        mock_tracker_class.return_value = mock_tracker

        # 2. Setup Vector Store Mock
        mock_qdrant_client = MagicMock()
        mock_qdrant_client.collection_exists.return_value = True
        mock_point = MagicMock()
        mock_point.id = "c1"
        mock_point.score = 0.92
        mock_point.payload = {
            "chunk_id": "c1",
            "doc_id": "doc1",
            "text": "Mitochondria undergo structural changes during leaf morphogenesis.",
        }
        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_response
        mock_qdrant_class.return_value = mock_qdrant_client

        # 3. Setup LLM Provider Mock
        mock_groq_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Mitochondria play a key role in programmed cell death."
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_groq_client.chat.completions.create.return_value = mock_completion
        mock_groq_class.return_value = mock_groq_client

        # 4. Ingestion & Chunking
        chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
        doc = ChunkDocument(
            doc_id="doc1",
            content="Mitochondria undergo structural changes during leaf morphogenesis.",
            source="pubmed",
            metadata={},
        )
        chunks = chunker.chunk(doc)
        assert len(chunks) > 0

        # 5. Embeddings & Vector Store Indexing
        embed_provider = EmbeddingFactory.get_provider("local", "BAAI/bge-large-en-v1.5")
        vstore = VectorStoreFactory.get_vector_store(
            "qdrant", "e2e_test_col", embed_provider.dimension
        )

        # 6. Retrieval & Reranking
        dense_ret = DenseRetriever(embed_provider=embed_provider, vector_store=vstore)
        bm25_ret = BM25Retriever(chunks=chunks)
        retriever = EnsembleRetriever(retrievers=[dense_ret, bm25_ret], rrf_k=60)

        # 7. Orchestration & LLM Generation
        llm = GroqLLMProvider(api_key="mock_key")
        pipeline = LinearRAGPipeline(retriever=retriever, llm_provider=llm)

        res = pipeline.run("What role do mitochondria play?")
        assert "Mitochondria" in res["answer"]
        assert len(res["retrieved_chunks"]) > 0

        # 8. RAGEvaluator Evaluation & Tracker Logging
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

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    @patch("rag_eval.generation.groq_provider.Groq")
    @patch("rag_eval.evaluation.tracker.MLflowTracker")
    def test_e2e_agentic_pipeline_flow(
        self, mock_tracker_class, mock_groq_class, mock_qdrant_class
    ):
        mock_tracker = MagicMock()
        mock_run = MagicMock()
        mock_run.info.run_id = "e2e-run-agentic-002"
        mock_tracker.start_run.return_value.__enter__.return_value = mock_run
        mock_tracker_class.return_value = mock_tracker

        mock_qdrant_client = MagicMock()
        mock_qdrant_client.collection_exists.return_value = True
        mock_point = MagicMock()
        mock_point.id = "c1"
        mock_point.score = 0.95
        mock_point.payload = {
            "chunk_id": "c1",
            "doc_id": "doc1",
            "text": "Mitochondrial permeability transition initiates cell death.",
        }
        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_qdrant_client.query_points.return_value = mock_response
        mock_qdrant_class.return_value = mock_qdrant_client

        mock_groq_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "yes"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]
        mock_groq_client.chat.completions.create.return_value = mock_completion
        mock_groq_class.return_value = mock_groq_client

        embed_provider = EmbeddingFactory.get_provider("local", "BAAI/bge-large-en-v1.5")
        vstore = VectorStoreFactory.get_vector_store(
            "qdrant", "e2e_agentic_col", embed_provider.dimension
        )

        chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
        doc = ChunkDocument(
            doc_id="doc1",
            content="Mitochondrial permeability transition initiates cell death.",
            source="pubmed",
            metadata={},
        )
        chunks = chunker.chunk(doc)

        dense_ret = DenseRetriever(embed_provider=embed_provider, vector_store=vstore)
        bm25_ret = BM25Retriever(chunks=chunks)
        retriever = EnsembleRetriever(retrievers=[dense_ret, bm25_ret], rrf_k=60)
        llm = GroqLLMProvider(api_key="mock_key")

        agentic_graph = AgenticRAGGraph(retriever=retriever, llm_provider=llm)
        res = agentic_graph.run("How do mitochondria initiate cell death?")

        assert "answer" in res
        assert len(res["retrieved_chunks"]) > 0
