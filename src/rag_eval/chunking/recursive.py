from rag_eval.chunking.base import BaseChunker
from rag_eval.chunking.schemas import Chunk, Document


class RecursiveCharacterChunker(BaseChunker):
    """
    Splits text recursively using a hierarchy of separators
    (e.g., double newlines, single newlines, sentences, spaces)
    to preserve semantic structure within target chunk size boundaries.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, document: Document) -> list[Chunk]:
        """Splits document content into chunks using recursive separator hierarchy."""
        if not document.content.strip():
            return []

        raw_text_splits = self._recursive_split(
            text=document.content,
            separators=self.separators,
        )

        merged_text_chunks = self._merge_splits_with_overlap(raw_text_splits)

        chunks: list[Chunk] = []
        for index, text in enumerate(merged_text_chunks):
            start_char = document.content.find(text)
            end_char = start_char + len(text) if start_char != -1 else None

            chunk_obj = self._build_chunk(
                document=document,
                chunk_text=text,
                chunk_index=index,
                start_char=start_char if start_char != -1 else None,
                end_char=end_char,
                extra_metadata={
                    "strategy": "recursive_character",
                    "chunk_size_target": self.chunk_size,
                },
            )
            chunks.append(chunk_obj)

        return chunks

    def _recursive_split(self, text: str, separators: list[str]) -> list[str]:
        """Recursively splits text using the first matching separator."""
        if len(text) <= self.chunk_size or not separators:
            return [text]

        separator = separators[0]
        next_separators = separators[1:]

        if separator in text:
            parts = text.split(separator)
        else:
            return self._recursive_split(text, next_separators)

        final_splits = []
        for part in parts:
            if len(part) > self.chunk_size:
                final_splits.extend(self._recursive_split(part, next_separators))
            elif part.strip():
                final_splits.append(part.strip())

        return final_splits

    def _merge_splits_with_overlap(self, splits: list[str]) -> list[str]:
        """Combines small splits into chunks up to self.chunk_size with overlap."""
        chunks = []
        current_chunk = ""

        for split in splits:
            if not current_chunk:
                current_chunk = split
            elif len(current_chunk) + len(split) + 1 <= self.chunk_size:
                current_chunk += " " + split
            else:
                chunks.append(current_chunk)
                overlap_text = (
                    current_chunk[-self.chunk_overlap :] if self.chunk_overlap > 0 else ""
                )
                current_chunk = (overlap_text + " " + split).strip()

        if current_chunk:
            chunks.append(current_chunk)

        return chunks
