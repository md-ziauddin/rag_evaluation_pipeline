"""
Factory for Instantiating Embedding Providers.
"""

from rag_eval.config.settings import settings
from rag_eval.embeddings.base import BaseEmbeddingProvider
from rag_eval.embeddings.bedrock import BedrockEmbeddingProvider
from rag_eval.embeddings.local import LocalEmbeddingProvider


class EmbeddingFactory:
    """
    Factory class creating provider instances based on configuration settings.
    """

    @staticmethod
    def get_provider(
        provider_type: str | None = None,
        model_name: str | None = None,
        dimension: int | None = None,
    ) -> BaseEmbeddingProvider:
        """
        Creates and returns an EmbeddingProvider instance.
        """
        p_type = provider_type or settings.DEFAULT_EMBEDDING_PROVIDER
        m_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        dim = dimension or 1024

        if p_type.lower() == "bedrock":
            return BedrockEmbeddingProvider(
                model_name=m_name,
                dimension=dim,
                region_name=settings.AWS_REGION,
            )
        elif p_type.lower() == "local":
            return LocalEmbeddingProvider(
                model_name=m_name,
                dimension=dim,
            )
        else:
            raise ValueError(f"Unsupported embedding provider type: {p_type}")
