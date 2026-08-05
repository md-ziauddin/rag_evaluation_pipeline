"""
Schemas for Vector Store Operations.
Defines the unified VectorSearchResult returned by Qdrant and Weaviate adapters.
"""

from typing import Any

from pydantic import BaseModel, Field


class VectorSearchResult(BaseModel):
    """
    Standardized search result item returned by any vector store implementation.

    Decouples retrieval algorithms from database-specific response objects
    (e.g., Qdrant ScoredPoint vs Weaviate QueryReturn).
    """

    chunk_id: str = Field(..., description="Unique identifier of the matching text chunk")
    doc_id: str = Field(..., description="ID of the parent document")
    text: str = Field(..., description="Raw text content of the chunk")
    score: float = Field(..., description="Similarity or relevance score (Higer is more relevant)")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional payload metadata (e.g. start_char, end_char, source,)",
    )
