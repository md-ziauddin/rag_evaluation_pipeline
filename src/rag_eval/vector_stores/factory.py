"""
Factory for Instantiating Vector Stores.
"""

from rag_eval.config.settings import settings
from rag_eval.vector_stores.base import BaseVectorStore
from rag_eval.vector_stores.qdrant_store import QdrantVectorStore
from rag_eval.vector_stores.weaviate_store import WeaviateVectorStore


class VectorStoreFactory:
    """
    Factory class creating vector store instances based on configuration settings.
    """

    @staticmethod
    def get_vector_store(
        store_type: str | None = None,
        collection_name: str = "pubmed_chunks",
        dimension: int = 1024,
    ) -> BaseVectorStore:
        """
        Creates and returns a BaseVectorStore adapter instance.
        """
        st_type = (store_type or "qdrant").lower()

        if st_type == "qdrant":
            return QdrantVectorStore(
                collection_name=collection_name,
                dimension=dimension,
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
        elif st_type == "weaviate":
            return WeaviateVectorStore(
                collection_name=collection_name,
                dimension=dimension,
                url=settings.WEAVIATE_URL,
                grpc_port=50051,
            )
        else:
            raise ValueError(f"Unsupported vector store type: {st_type}")
