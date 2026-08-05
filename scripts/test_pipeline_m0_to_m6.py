#!/usr/bin/env python3
"""
End-to-End Pipeline Verification: M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6.

Runs sample document through ingestion, chunking, embedding, vector store indexing,
retrieval/reranking, and dual RAG orchestration (Linear RAG & Agentic RAG).
"""

import os
import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.config.settings import settings
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.generation.base import BaseLLMProvider
from rag_eval.generation.groq_provider import GroqLLMProvider
from rag_eval.ingestion.pubmedqa import PubMedQALoader
from rag_eval.orchestration.agentic import AgenticRAGGraph
from rag_eval.orchestration.linear import LinearRAGPipeline
from rag_eval.retrieval.bm25 import BM25Retriever
from rag_eval.retrieval.dense import DenseRetriever
from rag_eval.retrieval.ensemble import EnsembleRetriever
from rag_eval.retrieval.rerankers import LocalReranker
from rag_eval.vector_stores.factory import VectorStoreFactory


class MockLLMProvider(BaseLLMProvider):
    """Fallback Mock LLM provider if external API key is not present."""

    def __init__(self):
        super().__init__(model_name="mock-llm-v1")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return (
            "Mitochondria play a pivotal role in PCD (programmed cell death) by regulating "
            "cellular energy and trigger signals during lace plant leaf remodelling."
        )


def main():
    print("===================================================================")
    print("   END-TO-END PIPELINE VERIFICATION: M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6")
    print("===================================================================")

    # Step 1: M0 Config
    print(f"\n[M0 Config] Environment: {settings.ENV}")

    # Step 2: M1 Ingestion
    print("\n[M1 Ingestion] Ingesting sample record from PubMedQA...")
    pubmed_loader = PubMedQALoader()
    docs, queries, qrels = pubmed_loader.process()
    sample_doc = docs[0]
    print(f"[M1 Ingestion] Ingested document ID: {sample_doc.id}")

    # Step 3: M2 Chunking
    print("\n[M2 Chunking] Splitting document into chunks...")
    chunk_doc = ChunkDocument(
        doc_id=sample_doc.id,
        content=sample_doc.text,
        source=sample_doc.source,
        metadata=sample_doc.metadata,
    )
    chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
    chunks = chunker.chunk(chunk_doc)
    print(f"[M2 Chunking] Generated {len(chunks)} text chunks.")

    # Step 4: M3 Embeddings
    print("\n[M3 Embeddings] Generating dense vectors via EmbeddingFactory...")
    embed_provider = EmbeddingFactory.get_provider(
        provider_type="local", model_name="BAAI/bge-large-en-v1.5"
    )
    chunk_texts = [c.text for c in chunks]
    vectors = embed_provider.embed_documents(chunk_texts)
    print(f"[M3 Embeddings] Generated {len(vectors)} vectors of dimension {len(vectors[0])}")

    # Step 5: M4 Vector Store Indexing
    print("\n[M4 Vector Stores] Initializing Qdrant Vector Store via Factory...")
    vector_store = VectorStoreFactory.get_vector_store(
        store_type="qdrant",
        collection_name="pipeline_verification_m6",
        dimension=embed_provider.dimension,
    )
    vector_store.create_collection(force_recreate=True)
    vector_store.index_chunks(chunks, vectors)
    print(f"[M4 Vector Stores] Indexed {len(chunks)} chunks in Qdrant.")

    query_text = queries[0].text
    print(f"\n[M5 Retrieval & Reranking] Search Query: '{query_text[:80]}...'")

    dense_retriever = DenseRetriever(embed_provider=embed_provider, vector_store=vector_store)
    bm25_retriever = BM25Retriever(chunks=chunks)
    ensemble_retriever = EnsembleRetriever(retrievers=[dense_retriever, bm25_retriever], rrf_k=60)
    reranker = LocalReranker(model_name="BAAI/bge-reranker-v2-m3")

    # Step 6: M6 LLM Provider & Orchestration Setup
    print("\n[M6 Generation] Initializing LLM Provider...")
    groq_key = settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")

    if groq_key:
        print("[M6 Generation] Using Groq API LLM Provider (llama-3.3-70b-versatile)...")
        llm_provider: BaseLLMProvider = GroqLLMProvider(api_key=groq_key)
    else:
        print("[M6 Generation] GROQ_API_KEY not found. Using MockLLMProvider for offline check...")
        llm_provider = MockLLMProvider()

    # Step 7A: M6 Linear RAG Pipeline
    print("\n-------------------------------------------------------------------")
    print("[M6 Linear RAG] Executing Retrieve -> Rerank -> Generate pipeline...")
    linear_pipeline = LinearRAGPipeline(
        retriever=ensemble_retriever,
        llm_provider=llm_provider,
        reranker=reranker,
    )
    linear_result = linear_pipeline.run(query_text)
    print(f"[M6 Linear RAG Answer]:\n{linear_result['answer']}\n")

    # Step 7B: M6 Agentic RAG Graph
    print("-------------------------------------------------------------------")
    print("[M6 Agentic RAG] Executing LangGraph state graph with self-correction loop...")
    agentic_graph = AgenticRAGGraph(
        retriever=ensemble_retriever,
        llm_provider=llm_provider,
        max_retries=2,
    )
    agentic_result = agentic_graph.run(query_text)
    print(f"[M6 Agentic RAG Answer]:\n{agentic_result['answer']}\n")
    print(f"[M6 Agentic RAG Info] Retry Count: {agentic_result['retry_count']}")

    print("\n===================================================================")
    print("   SUCCESS! PIPELINE M0 -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 FULLY CONNECTED")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
