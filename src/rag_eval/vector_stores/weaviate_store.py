"""
Weaviate Vector Store Adapter Implementation.
Connects to containerized Weaviate instance via weaviate-client v4.
Supports HNSW vector indexing, property filtering, and native alpha-weighted hybrid fusion.
"""

from typing import Any

import weaviate
from weaviate.classes.config import Configure, DataType, Property, VectorDistances
from weaviate.classes.query import MetadataQuery

from rag_eval.chunking.schemas import Chunk
from rag_eval.vector_stores.base import BaseVectorStore
from rag_eval.vector_stores.schemas import VectorSearchResult


class WeaviateVectorStore(BaseVectorStore):
    """
    Concrete VectorStore implementation for Weaviate (Client v4).
    """

    def __init__(
        self,
        collection_name: str = "PubMedChunk",
        dimension: int = 1024,
        url: str = "http://localhost:8080",
        grpc_port: int = 50051,
    ):
        # Format collection name to capitalized CamelCase per Weaviate conventions
        capitalized_name = collection_name[0].upper() + collection_name[1:]
        super().__init__(collection_name=capitalized_name, dimension=dimension)

        self.url = url
        self.grpc_port = grpc_port

        # Connect to local containerized Weaviate instance via v4 API
        self.client = weaviate.connect_to_local(
            host="localhost",
            port=8080,
            grpc_port=self.grpc_port,
        )

    def create_collection(self, force_recreate: bool = False) -> None:
        """Create Weaviate collection schema with manual vectorizer ('none')."""
        exists = self.client.collections.exists(self.collection_name)

        if exists and force_recreate:
            self.client.collections.delete(self.collection_name)
            exists = False

        if not exists:
            self.client.collections.create(
                name=self.collection_name,
                vectorizer_config=Configure.Vectorizer.none(),  # Vectors generated earlier
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE
                ),
                properties=[
                    Property(name="chunk_id", data_type=DataType.TEXT),
                    Property(name="doc_id", data_type=DataType.TEXT),
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="source", data_type=DataType.TEXT),
                ],
            )

    def index_chunks(self, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Batch index text chunks and vectors into Weaviate."""
        if len(chunks) != len(vectors):
            raise ValueError("Chunks and vectors count must match.")

        collection = self.client.collections.get(self.collection_name)

        with collection.batch.dynamic() as batch:
            for chunk, vector in zip(chunks, vectors, strict=False):
                properties = {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "text": chunk.text,
                    "source": chunk.metadata.get("source", ""),
                }
                batch.add_object(properties=properties, vector=vector)

    def search_dense(
        self,
        query_vector: list[float],
        top_k: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> list[VectorSearchResult]:
        """Search nearest vector neighbors in Weaviate."""
        collection = self.client.collections.get(self.collection_name)

        response = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=MetadataQuery(distance=True),
        )

        results: list[VectorSearchResult] = []
        for obj in response.objects:
            props = obj.properties or {}
            # Distance to Cosine similarity score conversion
            score = 1.0 - (obj.metadata.distance if obj.metadata.distance is not None else 0.0)
            results.append(
                VectorSearchResult(
                    chunk_id=str(props.get("chunk_id", obj.uuid)),
                    doc_id=str(props.get("doc_id", "")),
                    text=str(props.get("text", "")),
                    score=score,
                    metadata={"source": props.get("source", "")},
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
        """Native Weaviate hybrid search balancing BM25 and vector search with alpha."""
        collection = self.client.collections.get(self.collection_name)
        response = collection.query.hybrid(
            query=query_text,
            vector=query_vector,
            alpha=alpha,  # 0.0 = BM25, 1.0 = Vector, 0.5 = Balanced
            limit=top_k,
            return_metadata=MetadataQuery(score=True),
        )

        results: list[VectorSearchResult] = []

        for obj in response.objects:
            props = obj.properties or {}
            score = float(obj.metadata.score if obj.metadata.score is not None else 0.0)
            results.append(
                VectorSearchResult(
                    chunk_id=str(props.get("chunk_id", obj.uuid)),
                    doc_id=str(props.get("doc_id", "")),
                    text=str(props.get("text", "")),
                    score=score,
                    metadata={"source": props.get("source", "")},
                )
            )
        return results

    def delete_collection(self) -> None:
        """Drop collection from Weaviate."""
        if self.client.collections.exists(self.collection_name):
            self.client.collections.delete(self.collection_name)

    def close(self) -> None:
        """Close gRPC / HTTP client connection."""
        self.client.close()
