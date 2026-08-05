"""
Unit tests for Milestone 3 (M3) Embedding Providers.

Tests base interface, Bedrock provider mocking, local provider formatting,
disk caching, and provider factory instantiation.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from rag_eval.embeddings.bedrock import BedrockEmbeddingProvider
from rag_eval.embeddings.cache import EmbeddingCache
from rag_eval.embeddings.factory import EmbeddingFactory
from rag_eval.embeddings.local import LocalEmbeddingProvider


class TestEmbeddingCache:
    """Tests for file-based JSON embedding cache."""

    def test_cache_get_and_set(self, tmp_path: Path):
        cache = EmbeddingCache(cache_dir=tmp_path)
        model = "test-model"
        text = "Hello world"
        dim = 4
        vector = [0.1, 0.2, 0.3, 0.4]

        # Cache miss initially
        assert cache.get(model, text, dim) is None

        # Store in cache
        cache.set(model, text, dim, vector)

        # Cache hit
        cached_vector = cache.get(model, text, dim)
        assert cached_vector == vector


class TestLocalEmbeddingProvider:
    """Tests for LocalEmbeddingProvider formatting and inference logic."""

    @patch("rag_eval.embeddings.local.HAS_SENTENCE_TRANSFORMERS", True)
    @patch("rag_eval.embeddings.local.SentenceTransformer")
    def test_format_text_e5_prefixes(self, mock_st):
        provider = LocalEmbeddingProvider(model_name="intfloat/e5-large-v2", device="cpu")

        query_fmt = provider._format_text("Where is the heart?", is_query=True)
        passage_fmt = provider._format_text("The heart is in the chest.", is_query=False)

        assert query_fmt == "query: Where is the heart?"
        assert passage_fmt == "passage: The heart is in the chest."

    @patch("rag_eval.embeddings.local.HAS_SENTENCE_TRANSFORMERS", True)
    @patch("rag_eval.embeddings.local.SentenceTransformer")
    def test_format_text_bge_instructions(self, mock_st):
        provider = LocalEmbeddingProvider(model_name="BAAI/bge-large-en-v1.5", device="cpu")

        query_fmt = provider._format_text("What causes asthma?", is_query=True)
        doc_fmt = provider._format_text("Asthma is caused by inflammation.", is_query=False)

        assert "Represent this sentence" in query_fmt
        assert doc_fmt == "Asthma is caused by inflammation."

    @patch("rag_eval.embeddings.local.HAS_SENTENCE_TRANSFORMERS", True)
    @patch("rag_eval.embeddings.local.SentenceTransformer")
    def test_local_embed_documents_and_query(self, mock_st_class):
        mock_model = MagicMock()
        mock_model.encode.side_effect = [
            [[0.1, 0.2], [0.3, 0.4]],  # embed_documents response
            [0.5, 0.6],  # embed_query response
        ]
        mock_st_class.return_value = mock_model

        provider = LocalEmbeddingProvider(model_name="test-local-model", device="cpu")

        doc_vecs = provider.embed_documents(["doc1", "doc2"])
        assert doc_vecs == [[0.1, 0.2], [0.3, 0.4]]

        query_vec = provider.embed_query("query1")
        assert query_vec == [0.5, 0.6]


class TestBedrockEmbeddingProvider:
    """Tests for BedrockEmbeddingProvider boto3 invocation logic."""

    @patch("boto3.client")
    def test_bedrock_titan_embedding(self, mock_boto_client):
        mock_bedrock = MagicMock()
        mock_response = {
            "body": MagicMock(read=lambda: json.dumps({"embedding": [0.1, 0.2, 0.3]}).encode())
        }
        mock_bedrock.invoke_model.return_value = mock_response
        mock_boto_client.return_value = mock_bedrock

        provider = BedrockEmbeddingProvider(model_name="amazon.titan-embed-text-v2:0", dimension=3)

        vec = provider.embed_query("Medical text")
        assert vec == [0.1, 0.2, 0.3]
        mock_bedrock.invoke_model.assert_called_once()


class TestEmbeddingFactory:
    """Tests for EmbeddingFactory provider creation."""

    @patch("boto3.client")
    def test_get_bedrock_provider(self, mock_boto):
        provider = EmbeddingFactory.get_provider(provider_type="bedrock", model_name="titan")
        assert isinstance(provider, BedrockEmbeddingProvider)

    @patch("rag_eval.embeddings.local.HAS_SENTENCE_TRANSFORMERS", True)
    @patch("rag_eval.embeddings.local.SentenceTransformer")
    def test_get_local_provider(self, mock_st):
        provider = EmbeddingFactory.get_provider(provider_type="local", model_name="bge")
        assert isinstance(provider, LocalEmbeddingProvider)

    def test_unsupported_provider_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported embedding provider"):
            EmbeddingFactory.get_provider(provider_type="unknown_provider")
