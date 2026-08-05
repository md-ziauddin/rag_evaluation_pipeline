"""
Sparse BM25 Retriever Implementation (M5).

Uses BM25Okapi term frequency-inverse document frequency matching over text chunks.
"""

from rank_bm25 import BM25Okapi

from rag_eval.chunking.schemas import Chunk
from rag_eval.retrieval.base import BaseRetriever


class BM25Retriever(BaseRetriever):
    """
    Sparse keyword retriever using BM25Okapi algorithm.
    """

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks

        # Tokenize corpus text into lowercased word tokens
        corpus_tokens = [c.text.lower().split() for c in self.chunks]
        self.bm25 = BM25Okapi(corpus_tokens)

    def retrieve(self, query: str, top_k: int = 10) -> list[Chunk]:
        """Tokenize query and return top-k BM25 keyword matches."""
        query_tokens = query.lower().split()
        scores = self.bm25.get_scores(query_tokens)

        # Pair chunks with scores and sort in descending order
        scored_chunks = list(zip(self.chunks, scores, strict=False))
        scored_chunks.sort(key=lambda x: float(x[1]), reverse=True)

        return [chunk for chunk, score in scored_chunks[:top_k]]
