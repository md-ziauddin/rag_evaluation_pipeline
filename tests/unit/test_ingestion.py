"""
Unit tests for Milestone 1 (M1) Dataset Ingestion Pipeline.

Tests canonical schemas, loader process implementations (PubMedQA, MedQA),
and artifact versioning / SHA-256 manifest creation.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from rag_eval.ingestion.manifest import compute_file_sha256, create_manifest
from rag_eval.ingestion.medqa import MedQALoader
from rag_eval.ingestion.pubmedqa import PubMedQALoader
from rag_eval.ingestion.schemas import DatasetManifest, Document, Qrel, Query


class TestSchemas:
    """Tests for Pydantic canonical data contracts."""

    def test_document_immutability_and_defaults(self):
        doc = Document(
            id="pub_100_ctx_0",
            title="Test Title",
            text="Sample body text",
            source="pubmedqa",
        )
        assert doc.id == "pub_100_ctx_0"
        assert doc.metadata == {}

        from pydantic import ValidationError

        # Frozen model should disallow attribute assignment
        with pytest.raises(ValidationError):
            doc.text = "New text"

    def test_query_schema_with_options(self):
        query = Query(
            id="medqa_q_0",
            text="What is the diagnosis?",
            options={"A": "Flu", "B": "Cold"},
            gold_answer="A",
            source="medqa",
        )
        assert query.options == {"A": "Flu", "B": "Cold"}
        assert query.gold_answer == "A"

    def test_qrel_schema(self):
        qrel = Qrel(query_id="q1", document_id="d1", relevance=1)
        assert qrel.query_id == "q1"
        assert qrel.document_id == "d1"
        assert qrel.relevance == 1


class TestManifestAndVersioning:
    """Tests for artifact serialization and SHA-256 manifest generation."""

    def test_create_manifest(self, tmp_path: Path):
        docs = [Document(id="d1", text="text1", source="test")]
        queries = [Query(id="q1", text="q1 text", gold_answer="ans", source="test")]
        qrels = [Qrel(query_id="q1", document_id="d1", relevance=1)]

        manifest = create_manifest(
            output_dir=tmp_path,
            dataset_name="test_ds",
            version="v1.0.0",
            docs=docs,
            queries=queries,
            qrels=qrels,
        )

        assert isinstance(manifest, DatasetManifest)
        assert manifest.document_count == 1
        assert manifest.query_count == 1
        assert manifest.qrel_count == 1
        assert manifest.version == "v1.0.0"

        # Check JSONL files created
        docs_file = tmp_path / "test_ds_documents.jsonl"
        manifest_file = tmp_path / "test_ds_manifest.json"
        assert docs_file.exists()
        assert manifest_file.exists()

        # Check SHA256 integrity
        actual_hash = compute_file_sha256(docs_file)
        assert manifest.sha256_checksums["test_ds_documents.jsonl"] == actual_hash


class TestLoaders:
    """Tests for concrete dataset loaders."""

    @patch("rag_eval.ingestion.pubmedqa.load_dataset")
    def test_pubmedqa_loader_process(self, mock_load_dataset):
        mock_raw_item = {
            "pubid": 12345,
            "question": "Does Drug A work?",
            "long_answer": "Yes, Drug A works.",
            "context": {
                "contexts": ["Drug A is effective.", "No side effects found."],
                "labels": ["RESULTS", "CONCLUSION"],
                "meshes": ["Drug A", "Clinical Trial"],
            },
            "final_decision": "yes",
        }
        mock_load_dataset.return_value = [mock_raw_item]

        loader = PubMedQALoader()
        docs, queries, qrels = loader.process()

        assert len(queries) == 1
        assert queries[0].id == "pubmed_q_12345"
        assert queries[0].gold_answer == "Yes, Drug A works."

        assert len(docs) == 2
        assert docs[0].id == "pubmed_12345_ctx_0"
        assert docs[1].id == "pubmed_12345_ctx_1"

        assert len(qrels) == 2
        assert qrels[0].query_id == "pubmed_q_12345"
        assert qrels[0].document_id == "pubmed_12345_ctx_0"

    @patch("rag_eval.ingestion.medqa.load_dataset")
    def test_medqa_loader_process(self, mock_load_dataset):
        mock_raw_item = {
            "question": "What is the primary treatment for asthma?",
            "options": {"A": "Albuterol", "B": "Aspirin"},
            "answer": "Albuterol",
            "meta_info": "step1",
            "answer_idx": "A",
        }
        mock_load_dataset.return_value = [mock_raw_item]

        loader = MedQALoader()
        docs, queries, qrels = loader.process()

        assert len(docs) == 0  # Per ADR 0012, MedQA has no passage relevance
        assert len(qrels) == 0
        assert len(queries) == 1
        assert queries[0].gold_answer == "Albuterol"
        assert queries[0].options == {"A": "Albuterol", "B": "Aspirin"}
