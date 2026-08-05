"""
Local Open-Source Embedding Provider Implementation.
Uses sentence-transformers to execute open-source encoders locally:
- BGE (BAAI/bge-large-en-v1.5)
- E5 (intfloat/e5-large-v2) - auto-injects 'query: ' and 'passage: '
- Nomic (nomic-ai/nomic-embed-text-v1.5)
- Medical (MedCPT / PubMedBERT-based encoders)
"""

try:
    import torch

    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False

try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None
    HAS_SENTENCE_TRANSFORMERS = False

from rag_eval.embeddings.base import BaseEmbeddingProvider


class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """
    Concrete EmbeddingProvider for local sentence-transformers models.
    """

    def __init__(
        self,
        model_name: str = "BAAI/bge-large-en-v1.5",
        dimension: int = 1024,
        device: str | None = None,
    ):
        super().__init__(model_name=model_name, dimension=dimension)
        if not HAS_SENTENCE_TRANSFORMERS or SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers is required for LocalEmbeddingProvider. "
                "Install it with: pip install '.[local]'"
            )

        # Dynamically auto-detect GPU (cuda) if PyTorch/CUDA is available, otherwise fallback to CPU
        if device is not None:
            self.device = device
        elif HAS_TORCH and torch is not None and torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"

        # Load local sentence-transformer weights onto designated device
        self.model = SentenceTransformer(self.model_name, device=self.device)

    def _format_text(self, text: str, is_query: bool) -> str:
        """Applies model-specific prefixing rules to prevent quiet quality degradation."""
        lowered_name = self.model_name.lower()

        # E5 models strictly require 'query: ' or 'passage: ' prefixes
        if "e5" in lowered_name:
            prefix = "query: " if is_query else "passage: "
            return f"{prefix}{text}"

        # BGE models benefit from query instructions
        if "bge" in lowered_name and is_query:
            return f"Represent this sentence for searching relevant passages: {text}"

        return text

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed document passages locally using GPU/CPU."""
        if not texts:
            return []

        formatted_texts = [self._format_text(t, is_query=False) for t in texts]
        embeddings = self.model.encode(
            formatted_texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return [list(map(float, vec)) for vec in embeddings]

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query locally."""
        formatted_text = self._format_text(text, is_query=True)
        embedding = self.model.encode(
            formatted_text,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return list(map(float, embedding))
