from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Represents a full raw input document (e.g. a PubMed article or clinical guideline)
    before it gets split into chunks.

    # TODO: Implement PII/PHI scrubbing (de-identification) at the Document ingestion layer
    # BEFORE chunking and sending text to third-party embedding APIs (HIPAA/GDPR compliance).
    """

    doc_id: str = Field(
        ...,
        description="Unique identifier for the document (e.g. PubMed ID or file hash)",
    )
    content: str = Field(..., description="Raw text content of the document")
    source: str = Field(
        ...,
        description="Origin of the document (e.g. 'PubMed', 'MedQA', 'ClinicalNotes')",
    )
    publication_date: date | None = Field(
        default=None, description="Date of publication, if available"
    )
    medical_specialty: list[str] = Field(
        default_factory=list,
        description="Medical specialties tag list (e.g. ['Cardiology', 'Oncology'])",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary additional key-value metadata specific to source dataset",
    )


class Chunk(BaseModel):
    """
    Represents a text segment extracted from a parent Document.
    This is the unit that gets embedded and stored in vector databases (Qdrant / Weaviate).
    """

    chunk_id: str = Field(
        ...,
        description="Unique identifier for chunk (e.g., '{doc_id}_c{chunk_index}')",
    )
    doc_id: str = Field(..., description="Foreign key back to the parent Document.doc_id")
    text: str = Field(..., description="The text content of this individual chunk")
    chunk_index: int = Field(
        ...,
        description="Zero-based sequential index of chunk within parent document",
    )
    start_char: int | None = Field(
        default=None,
        description="Character offset where chunk starts in original document",
    )
    end_char: int | None = Field(
        default=None,
        description="Character offset where chunk ends in original document",
    )
    token_count: int | None = Field(
        default=None,
        description="Total token count for context-window and embedding limit checks",
    )
    parent_chunk_id: str | None = Field(
        default=None,
        description="Used for Parent-Child / Hierarchical chunking strategies",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata payload stored alongside vectors for filtering",
    )
