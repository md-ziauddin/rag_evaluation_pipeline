"""
Canonical Data Contracts for Ingestion.
These Pydantic models establish the strict schema boundary between raw datasets
and downstream RAG modules (Chunking, Vector Stores, Evaluation).
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Document(BaseModel):
    """
    Represents a raw text document/passage in the retrieval corpus.

    Attributes:
        id: Unique, deterministic identifier (e.g., 'pubmed_12345_ctx_0').
        title: Document or abstract title.
        text: Main body text of the document/passage.
        source: Source dataset origin ('pubmedqa' or 'medqa').
        metadata: Domain-specific metadata (mesh_terms, section_labels, year, etc.).
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Deterministic unique document ID")
    title: str = Field(default="", description="Document title")
    text: str = Field(..., description="Passage or document body text")
    source: str = Field(..., description="Dataset provenance tag")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata dictionary"
    )


class Query(BaseModel):
    """
    Represents an evaluation question/query.

    Attributes:
        id: Unique, deterministic query identifier.
        text: The question string asked by a user/evaluator.
        options: Multiple-choice options for datasets like MedQA (e.g., {'A': '...', 'B': '...'}).
        gold_answer: The ground truth answer string or option key (e.g., 'A' or 'Yes').
        source: Source dataset origin ('pubmedqa' or 'medqa').
        metadata: Domain metadata (e.g., question type, mesh headings).
    """

    model_config = ConfigDict(frozen=True)

    id: str = Field(..., description="Deterministic unique query ID")
    text: str = Field(..., description="Evaluation question string")
    options: dict[str, str] | None = Field(default=None, description="MCQ options if applicable")
    gold_answer: str = Field(..., description="Ground-truth target answer")
    source: str = Field(..., description="Dataset provenance tag")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata dictionary"
    )


class Qrel(BaseModel):
    """
    Query-Relevance Judgment (qrel) mapping a Query to a relevant Document.

    Used primarily by PubMedQA for Information Retrieval (IR) metrics calculation.
    """

    model_config = ConfigDict(frozen=True)
    query_id: str = Field(..., description="Foreign key to Query.id")
    document_id: str = Field(..., description="Foreign key to Document.id")
    relevance: int = Field(default=1, description="Graded relevance score (1 = relevant)")


class DatasetManifest(BaseModel):
    """
    Manifest file documenting the version, counts, and SHA-256 hashes of ingested artifacts.
    """

    dataset_name: str = Field(..., description="Name of the ingested dataset")
    version: str = Field(..., description="Pipeline/Dataset version tag")
    document_count: int = Field(..., description="Total corpus documents extracted")
    query_count: int = Field(..., description="Total evaluation queries extracted")
    qrel_count: int = Field(..., description="Total ground-truth qrel pairs created")
    sha256_checksums: dict[str, str] = Field(..., description="Map of filename to SHA-256 hash")
