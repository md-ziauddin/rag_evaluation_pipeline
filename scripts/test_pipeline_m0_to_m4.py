#!/usr/bin/env python3
"""
End-to-End Pipeline Verification: M0 -> M1 -> M2 -> M3 -> M4.

Runs sample document through ingestion, chunking, embedding, and vector store indexing
in both Qdrant and Weaviate.
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
from rag_eval.vector_stores.factory import VectorStoreFactory
from rag_eval.vector_stores.weaviate_store import WeaviateVectorStore


def main():
    print("===================================================================")
    print("   END-TO-END PIPELINE VERIFICATION: M0 -> M1 -> M2 -> M3 -> M4")
    print("===================================================================")

    # Step 1: M0 Config
    print(f"\n[M0 Config] Environment: {settings.ENV}")
    print(f"[M0 Config] Qdrant URL: {settings.QDRANT_URL} | Weaviate URL: {settings.WEAVIATE_URL}")

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

    query_text = queries[0].text
    print(f"\n[M3 Embeddings] Embedding search query: '{query_text[:80]}...'")
    query_vector = embed_provider.embed_query(query_text)

    # Step 5A: M4 Qdrant Vector Store Test
    print("\n-------------------------------------------------------------------")
    print("[M4 Qdrant] Initializing Qdrant Vector Store via Factory...")
    qdrant_store = VectorStoreFactory.get_vector_store(
        store_type="qdrant",
        collection_name="pipeline_verification_m4",
        dimension=embed_provider.dimension,
    )

    print("[M4 Qdrant] Creating collection schema...")
    qdrant_store.create_collection(force_recreate=True)

    print(f"[M4 Qdrant] Indexing {len(chunks)} chunks & vectors into Qdrant...")
    qdrant_store.index_chunks(chunks, vectors)

    print("[M4 Qdrant] Executing dense vector search...")
    qdrant_results = qdrant_store.search_dense(query_vector=query_vector, top_k=2)

    print(f"[M4 Qdrant] Retrieved {len(qdrant_results)} search results:")
    for i, res in enumerate(qdrant_results):
        print(f"  Result {i + 1}: chunk_id={res.chunk_id} | score={res.score:.4f}")
        print(f"    Text snippet: {res.text[:80]}...")

    # Step 5B: M4 Weaviate Vector Store Test
    print("\n-------------------------------------------------------------------")
    print("[M4 Weaviate] Initializing Weaviate Vector Store via Factory...")
    weaviate_store = VectorStoreFactory.get_vector_store(
        store_type="weaviate",
        collection_name="PubMedChunkTest",
        dimension=embed_provider.dimension,
    )

    print("[M4 Weaviate] Creating collection schema...")
    weaviate_store.create_collection(force_recreate=True)

    print(f"[M4 Weaviate] Indexing {len(chunks)} chunks & vectors into Weaviate...")
    weaviate_store.index_chunks(chunks, vectors)

    print("[M4 Weaviate] Executing dense vector search...")
    weaviate_dense_results = weaviate_store.search_dense(query_vector=query_vector, top_k=2)

    print(f"[M4 Weaviate Dense] Retrieved {len(weaviate_dense_results)} search results:")
    for i, res in enumerate(weaviate_dense_results):
        print(f"  Result {i + 1}: chunk_id={res.chunk_id} | score={res.score:.4f}")
        print(f"    Text snippet: {res.text[:80]}...")

    print("\n[M4 Weaviate] Executing native hybrid search (alpha=0.5)...")
    weaviate_hybrid_results = weaviate_store.search_hybrid(
        query_text=query_text, query_vector=query_vector, top_k=2, alpha=0.5
    )

    print(f"[M4 Weaviate Hybrid] Retrieved {len(weaviate_hybrid_results)} search results:")
    for i, res in enumerate(weaviate_hybrid_results):
        print(f"  Result {i + 1}: chunk_id={res.chunk_id} | score={res.score:.4f}")

    if isinstance(weaviate_store, WeaviateVectorStore):
        weaviate_store.close()

    print("\n===================================================================")
    print("   SUCCESS! PIPELINE M0 -> M1 -> M2 -> M3 -> M4 (QDRANT & WEAVIATE)")
    print("===================================================================\n")


if __name__ == "__main__":
    main()
