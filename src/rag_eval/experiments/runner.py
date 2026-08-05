"""
Experiment Runner Implementation.

Executes matrix combinations sequentially with caching/resume support and MLflow tracking.
"""

from typing import Any

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.evaluation.evaluator import RAGEvaluator
from rag_eval.evaluation.tracker import MLflowTracker
from rag_eval.generation.base import BaseLLMProvider
from rag_eval.generation.groq_provider import GroqLLMProvider
from rag_eval.orchestration.agentic import AgenticRAGGraph
from rag_eval.orchestration.linear import LinearRAGPipeline
from rag_eval.retrieval.bm25 import BM25Retriever
from rag_eval.retrieval.dense import DenseRetriever
from rag_eval.retrieval.ensemble import EnsembleRetriever
from rag_eval.vector_stores.factory import VectorStoreFactory


class MockLLMProvider(BaseLLMProvider):
    """Fallback LLM Provider for offline evaluation."""

    def __init__(self) -> None:
        super().__init__(model_name="mock-llm-v1")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return "Clinical answer based on context passages."


class ExperimentRunner:
    """
    Executes matrix evaluation sweeps and tracks runs in MLflow.
    """

    def __init__(self, tracker: MLflowTracker | None = None):
        self.tracker = tracker or MLflowTracker()
        self.evaluator = RAGEvaluator(tracker=self.tracker)

    def run_sweep(
        self,
        expanded_runs: list[dict[str, Any]],
        sample_docs: list[Any],
        test_cases: list[dict[str, Any]],
        experiment_name: str = "matrix_sweep",
    ) -> list[dict[str, Any]]:
        """
        Execute matrix sweep over expanded run configurations.
        """
        results: list[dict[str, Any]] = []

        for idx, run_params in enumerate(expanded_runs, start=1):
            vdb_name = run_params.get("vectorstore", "db")
            orch_name = run_params.get("orchestration", "linear")
            run_name = f"run_{idx}_{vdb_name}_{orch_name}"
            print(f"\n[M8 Runner] Executing Run {idx}/{len(expanded_runs)}: {run_name}...")

            # 1. Chunking Setup
            chunk_size = run_params.get("chunking_chunk_size", 300)
            chunk_overlap = run_params.get("chunking_chunk_overlap", 30)
            chunker = RecursiveCharacterChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            chunks = []
            for doc in sample_docs:
                chunk_doc = ChunkDocument(
                    doc_id=doc.id,
                    content=doc.text,
                    source=doc.source,
                    metadata=doc.metadata,
                )
                chunks.extend(chunker.chunk(chunk_doc))

            # 2. Embedding Provider
            embed_model = run_params.get("embedding_model", "BAAI/bge-large-en-v1.5")
            embed_provider = EmbeddingFactory.get_provider(
                provider_type="local" if "bge" in embed_model else "bedrock",
                model_name=embed_model,
            )

            chunk_texts = [c.text for c in chunks]
            vectors = embed_provider.embed_documents(chunk_texts)

            # 3. Vector Store
            store_type = run_params.get("vectorstore", "qdrant")
            vstore = VectorStoreFactory.get_vector_store(
                store_type=store_type,
                collection_name=f"m8_sweep_{idx}",
                dimension=embed_provider.dimension,
            )
            vstore.create_collection(force_recreate=True)
            vstore.index_chunks(chunks, vectors)

            # 4. Retrieval Setup
            dense_ret = DenseRetriever(embed_provider=embed_provider, vector_store=vstore)
            bm25_ret = BM25Retriever(chunks=chunks)
            retriever = EnsembleRetriever(retrievers=[dense_ret, bm25_ret], rrf_k=60)

            # 5. LLM Provider
            try:
                llm: BaseLLMProvider = GroqLLMProvider()
            except Exception:
                llm = MockLLMProvider()

            # 6. Orchestration Pipeline
            orchestration = run_params.get("orchestration", "linear")
            if orchestration == "agentic":
                pipeline: Any = AgenticRAGGraph(retriever=retriever, llm_provider=llm)
            else:
                pipeline = LinearRAGPipeline(retriever=retriever, llm_provider=llm)

            # 7. Evaluate and Log to MLflow
            eval_res = self.evaluator.evaluate_pipeline(
                pipeline=pipeline,
                test_cases=test_cases,
                run_name=run_name,
                pipeline_params=run_params,
            )

            results.append(
                {
                    "run_name": run_name,
                    "run_id": eval_res["run_id"],
                    "params": run_params,
                    "metrics": eval_res["metrics"],
                }
            )

        return results
