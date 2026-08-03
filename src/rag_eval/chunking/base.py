from abc import abstractmethod, ABC
from typing import Any, Dict, List
from rag_eval.chunking.data_contract import Document, Chunk

class BaseChunker(ABC):
    """
    Abstract Base Class for all chunking strategies.
    
    Every chunker strategy (Fixed, Recursive, Medical Section-Aware, etc.) 
    must inherit from this class and implement the `chunk` method.
    """

    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
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
        extra_metadata: Dict[str, Any] | None = None,
    ) -> Chunk:
        """
        Helper method to construct a standard Chunk object.
        
        Ensures consistent chunk_id formatting and metadata inheritance
        from the parent Document down to the Chunk.
        """

        # 1. Inherit document metadata and merge any chunk-specific metadata
        chunk_metadata = {
            "source": document.source,
            "medical_specialty": document.medical_specialty,
            **document.metadata, # Include parent document's extra metadata
            **(extra_metadata or {}), # Merge chunk_level extra metadata
        }

        # 2 Construct deterministic chunk ID
        chunk_id = f"{document.doc_id}_c{chunk_index}"

        return Chunk(
            chunk_id=chunk_id,
            doc_id=document.doc_id,
            text=chunk_text,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            token_count=len(chunk_text.split()), # simple token count heuristic
            metadata=chunk_metadata
            
        )

    