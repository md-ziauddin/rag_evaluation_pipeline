"""
Unit tests for Milestone 4 (M4) Vector Stores (Qdrant & Weaviate).

Tests schemas, Qdrant adapter mocking, Weaviate adapter mocking, and factory creation.
"""

from unittest.mock import MagicMock, patch

import pytest

from rag_eval.chunking.schemas import Chunk
from rag_eval.vector_stores.factory import VectorStoreFactory
from rag_eval.vector_stores.qdrant_store import QdrantVectorStore
from rag_eval.vector_stores.schemas import VectorSearchResult
from rag_eval.vector_stores.weaviate_store import WeaviateVectorStore


class TestVectorStoreSchemas:
    """Tests for VectorSearchResult schema."""

    def test_vector_search_result_instantiation(self):
        res = VectorSearchResult(
            chunk_id="chunk_101",
            doc_id="doc_1",
            text="Heart failure treatment involves ACE inhibitors.",
            score=0.92,
            metadata={"source": "pubmed"},
        )
        assert res.chunk_id == "chunk_101"
        assert res.doc_id == "doc_1"
        assert res.score == 0.92
        assert res.metadata["source"] == "pubmed"


class TestQdrantVectorStore:
    """Tests for QdrantVectorStore adapter."""

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_create_collection(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = False
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=512)
        store.create_collection()

        mock_client.collection_exists.assert_called_with("test_col")
        mock_client.create_collection.assert_called_once()

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_create_collection_force_recreate(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=512)
        store.create_collection(force_recreate=True)

        mock_client.delete_collection.assert_called_with("test_col")
        mock_client.create_collection.assert_called_once()

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_index_chunks(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=2)
        chunks = [
            Chunk(chunk_id="c1", doc_id="d1", chunk_index=0, text="Chunk text 1", token_count=4),
            Chunk(chunk_id="c2", doc_id="d1", chunk_index=1, text="Chunk text 2", token_count=4),
        ]
        vectors = [[0.1, 0.2], [0.3, 0.4]]

        store.index_chunks(chunks, vectors)
        mock_client.upsert.assert_called_once()

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_index_chunks_mismatched_length_raises_error(self, mock_qdrant_class):
        store = QdrantVectorStore(collection_name="test_col", dimension=2)
        chunks = [Chunk(chunk_id="c1", doc_id="d1", chunk_index=0, text="Text", token_count=1)]
        vectors = [[0.1, 0.2], [0.3, 0.4]]

        with pytest.raises(ValueError, match="Chunks and vectors count must match"):
            store.index_chunks(chunks, vectors)

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_search_dense(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_point = MagicMock()
        mock_point.id = "c1"
        mock_point.score = 0.88
        mock_point.payload = {"chunk_id": "c1", "doc_id": "d1", "text": "Heart disease context"}

        mock_response = MagicMock()
        mock_response.points = [mock_point]
        mock_client.query_points.return_value = mock_response
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=2)
        results = store.search_dense(query_vector=[0.1, 0.2], top_k=1)

        assert len(results) == 1
        assert results[0].chunk_id == "c1"
        assert results[0].score == 0.88

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_search_hybrid(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_point1 = MagicMock()
        mock_point1.id = "c1"
        mock_point1.score = 0.88
        mock_point1.payload = {
            "chunk_id": "c1",
            "doc_id": "d1",
            "text": "Asthma inhalers treatment",
        }

        mock_point2 = MagicMock()
        mock_point2.id = "c2"
        mock_point2.score = 0.65
        mock_point2.payload = {"chunk_id": "c2", "doc_id": "d2", "text": "Diabetes insulin therapy"}

        mock_response = MagicMock()
        mock_response.points = [mock_point1, mock_point2]
        mock_client.query_points.return_value = mock_response
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=2)
        results = store.search_hybrid(
            query_text="asthma inhalers", query_vector=[0.1, 0.2], top_k=2
        )

        assert len(results) == 2
        assert results[0].chunk_id == "c1"

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_delete_collection(self, mock_qdrant_class):
        mock_client = MagicMock()
        mock_client.collection_exists.return_value = True
        mock_qdrant_class.return_value = mock_client

        store = QdrantVectorStore(collection_name="test_col", dimension=2)
        store.delete_collection()

        mock_client.delete_collection.assert_called_with("test_col")


class TestWeaviateVectorStore:
    """Tests for WeaviateVectorStore adapter."""

    @patch("weaviate.connect_to_local")
    def test_create_collection(self, mock_connect):
        mock_client = MagicMock()
        mock_client.collections.exists.return_value = False
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=512)
        store.create_collection()

        mock_client.collections.exists.assert_called_with("PubMedChunk")
        mock_client.collections.create.assert_called_once()

    @patch("weaviate.connect_to_local")
    def test_create_collection_force_recreate(self, mock_connect):
        mock_client = MagicMock()
        mock_client.collections.exists.return_value = True
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=512)
        store.create_collection(force_recreate=True)

        mock_client.collections.delete.assert_called_with("PubMedChunk")
        mock_client.collections.create.assert_called_once()

    @patch("weaviate.connect_to_local")
    def test_index_chunks(self, mock_connect):
        mock_client = MagicMock()
        mock_collection = MagicMock()
        mock_batch = MagicMock()

        # Context manager mock for collection.batch.dynamic()
        mock_collection.batch.dynamic.return_value.__enter__.return_value = mock_batch
        mock_client.collections.get.return_value = mock_collection
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        chunks = [
            Chunk(chunk_id="c1", doc_id="d1", chunk_index=0, text="Weaviate 1", token_count=3),
            Chunk(chunk_id="c2", doc_id="d1", chunk_index=1, text="Weaviate 2", token_count=3),
        ]
        vectors = [[0.1, 0.2], [0.3, 0.4]]

        store.index_chunks(chunks, vectors)
        assert mock_batch.add_object.call_count == 2

    @patch("weaviate.connect_to_local")
    def test_index_chunks_mismatched_length_raises_error(self, mock_connect):
        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        chunks = [Chunk(chunk_id="c1", doc_id="d1", chunk_index=0, text="Text", token_count=1)]
        vectors = [[0.1, 0.2], [0.3, 0.4]]

        with pytest.raises(ValueError, match="Chunks and vectors count must match"):
            store.index_chunks(chunks, vectors)

    @patch("weaviate.connect_to_local")
    def test_search_dense(self, mock_connect):
        mock_client = MagicMock()
        mock_obj = MagicMock()
        mock_obj.uuid = "uuid-1"
        mock_obj.properties = {"chunk_id": "c1", "doc_id": "d1", "text": "Weaviate text"}
        mock_obj.metadata.distance = 0.15

        mock_collection = MagicMock()
        mock_collection.query.near_vector.return_value.objects = [mock_obj]
        mock_client.collections.get.return_value = mock_collection
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        results = store.search_dense(query_vector=[0.1, 0.2], top_k=1)

        assert len(results) == 1
        assert results[0].chunk_id == "c1"
        assert abs(results[0].score - 0.85) < 1e-4

    @patch("weaviate.connect_to_local")
    def test_search_hybrid(self, mock_connect):
        mock_client = MagicMock()
        mock_obj = MagicMock()
        mock_obj.uuid = "uuid-2"
        mock_obj.properties = {"chunk_id": "c2", "doc_id": "d1", "text": "Hybrid text"}
        mock_obj.metadata.score = 0.76

        mock_collection = MagicMock()
        mock_collection.query.hybrid.return_value.objects = [mock_obj]
        mock_client.collections.get.return_value = mock_collection
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        results = store.search_hybrid(
            query_text="asthma treatment", query_vector=[0.1, 0.2], top_k=1, alpha=0.5
        )

        assert len(results) == 1
        assert results[0].chunk_id == "c2"
        assert results[0].score == 0.76

    @patch("weaviate.connect_to_local")
    def test_delete_collection(self, mock_connect):
        mock_client = MagicMock()
        mock_client.collections.exists.return_value = True
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        store.delete_collection()

        mock_client.collections.delete.assert_called_with("PubMedChunk")

    @patch("weaviate.connect_to_local")
    def test_close_connection(self, mock_connect):
        mock_client = MagicMock()
        mock_connect.return_value = mock_client

        store = WeaviateVectorStore(collection_name="PubMedChunk", dimension=2)
        store.close()

        mock_client.close.assert_called_once()


class TestVectorStoreFactory:
    """Tests for VectorStoreFactory creation."""

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    def test_get_qdrant_store(self, mock_qdrant):
        store = VectorStoreFactory.get_vector_store(store_type="qdrant")
        assert isinstance(store, QdrantVectorStore)

    @patch("weaviate.connect_to_local")
    def test_get_weaviate_store(self, mock_weaviate):
        store = VectorStoreFactory.get_vector_store(store_type="weaviate")
        assert isinstance(store, WeaviateVectorStore)

    def test_invalid_store_raises_error(self):
        with pytest.raises(ValueError, match="Unsupported vector store type"):
            VectorStoreFactory.get_vector_store(store_type="unknown_db")
