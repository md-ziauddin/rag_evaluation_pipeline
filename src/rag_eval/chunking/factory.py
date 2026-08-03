from typing import Any, Dict, Type
from rag_eval.chunking.base import BaseChunker
from rag_eval.chunking.recursive import RecursiveCharacterChunker

class ChunkerFactory:
    """
    Factory class to dynamically instantiate chunkers based on strategy name.
    """

    _register: Dict[str, Type[BaseChunker]] = {
        "recursive": RecursiveCharacterChunker
        # Future strategies added here:
        # "fixed": FixedSizeChunker,
        # "medical_section": MedicalSectionChunker,
    }

    @classmethod
    def register(cls, name: str, chunker_cls: Type[BaseChunker]) -> None:
        """Allows registering custom external chunking strategies at runtime."""
        cls._register[name.lower()] = chunker_cls

    @classmethod
    def get_chunker(cls, name: str, **kwargs: Any) -> BaseChunker:
        """
        Instantiates and returns a chunker strategy by name.
        
        Example:
            chunker = ChunkerFactory.get_chunker("recursive", chunk_size=500, chunk_overlap=50)
        """
        key = name.lower()
        if key not in cls._register:
            valid_keys = list(cls._register.keys())
            raise ValueError(f"Unknown Chunking strategy '{name}'. Available strategies: {valid_keys}")

        return cls._register[key](**kwargs)