from abc import ABC, abstractmethod
from typing import Any

from rag_eval.chunking.schemas import Chunk, Document


class BaseChunker(ABC):
    """
    Abstract Base Class for all chunking strategies.

    Every chunker strategy (Fixed, Recursive, Medical Section-Aware, etc.)
    must inherit from this class and implement the `chunk` method.
    """

    @abstractmethod
    def chunk(self, document: Document) -> list[Chunk]:
        """
        Splits a Document into a list of Chunk objects.

        Must be implemented by all concrete chunking subclasses.
        """
        pass

    def _build_chunk(
        self,
        document: Document,
        chunk_text: str,
        chunk_index: int,
        start_char: int | None = None,
        end_char: int | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> Chunk:
        """
        Helper method to construct a standard Chunk object.

        Ensures consistent chunk_id formatting and metadata inheritance
        from the parent Document down to the Chunk.
        """
        chunk_metadata = {
            "source": document.source,
            "medical_specialty": document.medical_specialty,
            **document.metadata,
            **(extra_metadata or {}),
        }

        chunk_id = f"{document.doc_id}_c{chunk_index}"

        return Chunk(
            chunk_id=chunk_id,
            doc_id=document.doc_id,
            text=chunk_text,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            token_count=len(chunk_text.split()),
            metadata=chunk_metadata,
        )
