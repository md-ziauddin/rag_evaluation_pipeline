#!/usr/bin/env python3
"""
End-to-End Pipeline Verification: M0 (Config) -> M1 (Ingestion) -> M2 (Chunking) -> M3 (Embeddings).

Runs a sample document through ingestion, recursive chunking, and embedding generation
with disk cache verification.
"""

import sys
from pathlib import Path

# Add src to pythonpath
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rag_eval.chunking.recursive import RecursiveCharacterChunker
from rag_eval.chunking.schemas import Document as ChunkDocument
from rag_eval.config.settings import settings
from rag_eval.embeddings.cache import EmbeddingCache
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.ingestion.pubmedqa import PubMedQALoader


def main():
    print("========================================================")
    print("   END-TO-END PIPELINE VERIFICATION: M0 -> M1 -> M2 -> M3")
    print("========================================================")

    # Step 1: M0 Configuration Verification
    print(f"\n[M0 Config] Environment: {settings.ENV} | AWS Region: {settings.AWS_REGION}")
    print(f"[M0 Config] Default Provider: {settings.DEFAULT_EMBEDDING_PROVIDER}")

    # Step 2: M1 Data Ingestion (Sample item from PubMedQA)
    print("\n[M1 Ingestion] Loading sample record from PubMedQA dataset...")
    pubmed_loader = PubMedQALoader()
    docs, queries, qrels = pubmed_loader.process()
    sample_doc = docs[0]
    print(f"[M1 Ingestion] Ingested document ID: {sample_doc.id}")
    print(f"[M1 Ingestion] Title: {sample_doc.title}")
    print(f"[M1 Ingestion] Text sample: {sample_doc.text[:120]}...")

    # Step 3: M2 Document Chunking
    print("\n[M2 Chunking] Splitting Document using RecursiveCharacterChunker...")
    chunk_doc = ChunkDocument(
        doc_id=sample_doc.id,
        content=sample_doc.text,
        source=sample_doc.source,
        metadata=sample_doc.metadata,
    )
    chunker = RecursiveCharacterChunker(chunk_size=300, chunk_overlap=30)
    chunks = chunker.chunk(chunk_doc)
    print(f"[M2 Chunking] Created {len(chunks)} text chunks from document.")
    for i, c in enumerate(chunks):
        print(f"  - Chunk {i} [{c.chunk_id}]: len={len(c.text)} chars | tokens~={c.token_count}")

    # Step 4: M3 Embedding Provider & Cache Verification
    print("\n[M3 Embeddings] Instantiating Embedding Provider via Factory...")
    # Default to Local provider for self-contained test execution
    provider = EmbeddingFactory.get_provider(
        provider_type="local", model_name="BAAI/bge-large-en-v1.5"
    )
    print(f"[M3 Embeddings] Provider: {provider.__class__.__name__} | Device: {provider.device}")

    # Embed document chunks
    chunk_texts = [c.text for c in chunks]
    print(f"[M3 Embeddings] Embedding {len(chunk_texts)} chunk texts...")
    embeddings = provider.embed_documents(chunk_texts)
    print(f"[M3 Embeddings] Generated {len(embeddings)} vectors of dimension {len(embeddings[0])}")

    # Embed search query
    query_text = queries[0].text
    print(f"\n[M3 Embeddings] Embedding Query: '{query_text[:80]}...'")
    query_vector = provider.embed_query(query_text)
    print(f"[M3 Embeddings] Query Vector dimension: {len(query_vector)}")

    # Test Embedding Cache
    print("\n[M3 Cache] Testing EmbeddingCache disk persistence...")
    cache = EmbeddingCache()
    cache.set(provider.model_name, query_text, provider.dimension, query_vector)
    cached_vec = cache.get(provider.model_name, query_text, provider.dimension)
    assert cached_vec == query_vector
    print("[M3 Cache] Cache verification successful! SHA-256 key retrieved matches exact vector.")

    print("\n========================================================")
    print("   SUCCESS! PIPELINE M0 -> M1 -> M2 -> M3 FULLY CONNECTED")
    print("========================================================\n")


if __name__ == "__main__":
    main()
