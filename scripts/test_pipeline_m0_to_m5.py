#!/usr/bin/env python3
"""
End-to-End Pipeline Verification: M0 -> M1 -> M2 -> M3 -> M4 -> M5.

Runs a sample document through ingestion, chunking, embedding, vector store indexing,
retrieval (Dense, BM25, RRF Ensemble), and candidate reranking.
"""

import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.config.settings import settings
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.ingestion.pubmedqa import PubMedQALoader
from rag_eval.retrieval.bm25 import BM25Retriever
from rag_eval.retrieval.dense import DenseRetriever
from rag_eval.retrieval.ensemble import EnsembleRetriever
from rag_eval.retrieval.rerankers import LocalReranker
from rag_eval.vector_stores.factory import VectorStoreFactory


def main():
    print("===================================================================")
    print("   END-TO-END PIPELINE VERIFICATION: M0 -> M1 -> M2 -> M3 -> M4 -> M5")
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
        collection_name="pipeline_verification_m5",
        dimension=embed_provider.dimension,
    )
    vector_store.create_collection(force_recreate=True)
    vector_store.index_chunks(chunks, vectors)
    print(f"[M4 Vector Stores] Indexed {len(chunks)} chunks in Qdrant.")

    query_text = queries[0].text
    print(f"\n[M5 Retrieval] Search Query: '{query_text[:80]}...'")

    # Step 6A: Dense Retriever
    dense_retriever = DenseRetriever(embed_provider=embed_provider, vector_store=vector_store)
    dense_results = dense_retriever.retrieve(query_text, top_k=2)
    print(f"[M5 Dense Retrieval] Retrieved {len(dense_results)} chunks.")

    # Step 6B: BM25 Retriever
    bm25_retriever = BM25Retriever(chunks=chunks)
    bm25_results = bm25_retriever.retrieve(query_text, top_k=2)
    print(f"[M5 BM25 Retrieval] Retrieved {len(bm25_results)} chunks.")

    # Step 6C: Ensemble RRF Retriever
    ensemble_retriever = EnsembleRetriever(retrievers=[dense_retriever, bm25_retriever], rrf_k=60)
    ensemble_results = ensemble_retriever.retrieve(query_text, top_k=2)
    print(f"[M5 Ensemble RRF Retrieval] Retrieved {len(ensemble_results)} fused chunks:")
    for i, res in enumerate(ensemble_results):
        print(f"  Rank {i + 1}: chunk_id={res.chunk_id} | snippet={res.text[:80]}...")

    # Step 6D: Local Cross-Encoder Reranker (GPU accelerated)
    print("\n[M5 Reranking] Initializing Local Cross-Encoder Reranker...")
    reranker = LocalReranker(model_name="BAAI/bge-reranker-v2-m3")
    print(f"[M5 Reranking] Reranker Device: {reranker.device}")

    reranked_chunks = reranker.rerank(query_text, ensemble_results, top_n=1)
    print(f"[M5 Reranking] Top 1 Reranked Chunk: ID={reranked_chunks[0].chunk_id}")
    print(f"  Text: {reranked_chunks[0].text}")

    print("\n===================================================================")
    print("   SUCCESS! PIPELINE M0 -> M1 -> M2 -> M3 -> M4 -> M5 FULLY CONNECTED")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
