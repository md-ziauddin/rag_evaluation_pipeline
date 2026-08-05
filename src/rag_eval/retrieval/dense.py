"""
Dense Vector Retriever Implementation (M5).

Translates query text into a vector using EmbeddingProvider (M3) and searches
nearest neighbors in BaseVectorStore (M4).
"""

from rag_eval.chunking.schemas import Chunk
from rag_eval.embeddings.base import BaseEmbeddingProvider
from rag_eval.retrieval.base import BaseRetriever
from rag_eval.vector_stores.base import BaseVectorStore


class DenseRetriever(BaseRetriever):
    """
    Dense semantic retriever executing vector similarity search against Qdrant or Weaviate.
    """

    def __init__(
        self,
        embed_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ):
        self.embed_provider = embed_provider
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 10) -> list[Chunk]:
        """Embed query and search vector store nearest neighbors."""
        # Step 1: Embed query into a 1024-dim dense vector
        query_vector = self.embed_provider.embed_query(query)

        # Step 2: Search vector database
        search_results = self.vector_store.search_dense(
            query_vector=query_vector,
            top_k=top_k,
        )

        # Step 3: Map VectorSearchResult items back to Chunk objects
        chunks: list[Chunk] = []
        for i, res in enumerate(search_results):
            chunks.append(
                Chunk(
                    chunk_id=res.chunk_id,
                    doc_id=res.doc_id,
                    chunk_index=i,
                    text=res.text,
                    token_count=len(res.text.split()),
                    metadata=res.metadata,
                )
            )
        return chunks
