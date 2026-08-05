"""
Qdrant Vector Store Adapter Implementation.

Connects to containerized Qdrant instance via qdrant-client.
Supports HNSW vector indexing, payload metadata filtering, and RRF hybrid fusion.
"""

import uuid
from typing import Any

from qdrant_client import QdrantClient, models

from rag_eval.chunking.schemas import Chunk
from rag_eval.vector_stores.base import BaseVectorStore
from rag_eval.vector_stores.schemas import VectorSearchResult


class QdrantVectorStore(BaseVectorStore):
    """
    Concrete VectorStore implementation for Qdrant.
    """

    def __init__(
        self,
        collection_name: str = "pubmed_chunks",
        dimension: int = 1024,
        url: str = "http://localhost:6333",
        api_key: str | None = None,
    ):
        super().__init__(collection_name=collection_name, dimension=dimension)
        self.url = url
        self.client = QdrantClient(url=self.url, api_key=api_key)

    def create_collection(self, force_recreate: bool = False) -> None:
        """Create Qdrant collection with Cosine distance and HNSW index."""
        exists = self.client.collection_exists(self.collection_name)

        if exists and force_recreate:
            self.client.delete_collection(self.collection_name)
            exists = False

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    def index_chunks(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Upsert text chunks and dense vectors into Qdrant."""
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors count must match.")

        points: list[models.PointStruct] = []
        for chunk, vector in zip(chunks, vectors, strict=False):
            # Convert string ID or generate deterministic UUID for Qdrant point
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
            payload = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "text": chunk.text,
                "source": chunk.metadata.get("source", ""),
                "token_count": chunk.token_count,
                "metadata": chunk.metadata,
            }
            points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))
        self.client.upsert(collection_name=self.collection_name, points=points)

    def _build_filter(self, filters: dict[str, Any] | None) -> models.Filter | None:
        """Convert dictionary filters to Qdrant Filter objects."""
        if not filters:
            return None

        must_conditions: list[Any] = [
            models.FieldCondition(key=k, match=models.MatchValue(value=v))
            for k, v in filters.items()
        ]
        return models.Filter(must=must_conditions)

    def search_dense(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search nearest vector neighbors in Qdrant."""
        q_filter = self._build_filter(filters)
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=q_filter,
        )
        results: list[VectorSearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                VectorSearchResult(
                    chunk_id=str(payload.get("chunk_id", str(point.id))),
                    doc_id=str(payload.get("doc_id", "")),
                    text=str(payload.get("text", "")),
                    score=float(point.score),
                    metadata=dict(payload.get("metadata", {})),
                )
            )
        return results

    def search_hybrid(
        self,
        query_text: str,
        query_vector: list[float],
        top_k: int = 10,
        alpha: float = 0.5,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """
        Qdrant dense similarity search (Fallback/Default dense path).
        Full hybrid search in Qdrant will combine sparse indices.

        @TODO: Need to update this method to use the sparse indices built in M5 and use RRF/DBSF fusion.
        """
        return self.search_dense(query_vector=query_vector, top_k=top_k, filters=filters)

    def delete_collection(self) -> None:
        """Delete Qdrant collection."""
        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)
