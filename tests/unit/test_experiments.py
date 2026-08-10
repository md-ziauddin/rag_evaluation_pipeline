"""
Unit tests for Milestone 8 (M8) Experiment Runner, Matrix Expander, and Comparison Reporter.

Tests MatrixExpander, ExperimentRunner, and ComparisonReporter.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from rag_eval.experiments.matrix import MatrixExpander
from rag_eval.experiments.reporter import ComparisonReporter
from rag_eval.experiments.runner import ExperimentRunner


class TestMatrixExpander:
    """Tests for MatrixExpander."""

    def test_matrix_expansion(self, tmp_path):
        yaml_file = tmp_path / "test_exp.yaml"
        yaml_file.write_text(
            """
experiment:
  name: test_matrix
matrix:
  vectorstore: [qdrant, weaviate]
  orchestration: [linear, agentic]
"""
        )

        expander = MatrixExpander(config_path=yaml_file)
        runs = expander.expand()

        assert len(runs) == 4
        # Verify Cartesian product (2 x 2 = 4)
        run_combos = {(r["vectorstore"], r["orchestration"]) for r in runs}
        assert run_combos == {
            ("qdrant", "linear"),
            ("qdrant", "agentic"),
            ("weaviate", "linear"),
            ("weaviate", "agentic"),
        }


class TestComparisonReporter:
    """Tests for ComparisonReporter."""

    def test_generate_report(self, tmp_path):
        reporter = ComparisonReporter(output_dir=tmp_path)
        run_results = [
            {
                "run_name": "run_1_qdrant",
                "params": {
                    "vectorstore": "qdrant",
                    "embedding_model": "bge",
                    "orchestration": "linear",
                },
                "metrics": {"ndcg_at_10": 0.85, "faithfulness": 0.90, "avg_latency_ms": 300.0},
            },
            {
                "run_name": "run_2_weaviate",
                "params": {
                    "vectorstore": "weaviate",
                    "embedding_model": "bge",
                    "orchestration": "agentic",
                },
                "metrics": {"ndcg_at_10": 0.90, "faithfulness": 0.95, "avg_latency_ms": 450.0},
            },
        ]

        report_file = reporter.generate_report(run_results)
        assert Path(report_file).exists()

        content = (tmp_path / "comparison_report.md").read_text()
        assert "Medical RAG Experiment Comparison Report" in content
        assert "run_2_weaviate" in content


class TestExperimentRunner:
    """Tests for ExperimentRunner."""

    @patch("rag_eval.vector_stores.qdrant_store.QdrantClient")
    @patch("rag_eval.experiments.runner.RAGEvaluator")
    def test_run_sweep(self, mock_evaluator_class, mock_qdrant_class):
        mock_qdrant_client = MagicMock()
        mock_qdrant_client.collection_exists.return_value = True
        mock_qdrant_class.return_value = mock_qdrant_client

        mock_evaluator = MagicMock()
        mock_evaluator.evaluate_pipeline.return_value = {
            "run_id": "run-123",
            "metrics": {"ndcg_at_10": 0.85, "faithfulness": 0.90, "avg_latency_ms": 250.0},
        }
        mock_evaluator_class.return_value = mock_evaluator

        runner = ExperimentRunner()
        expanded_runs = [{"vectorstore": "qdrant", "orchestration": "linear"}]
        mock_doc = MagicMock()
        mock_doc.id = "doc1"
        mock_doc.text = "Context"
        mock_doc.source = "pubmed"
        mock_doc.metadata = {}

        results = runner.run_sweep(
            expanded_runs=expanded_runs,
            sample_docs=[mock_doc],
            test_cases=[{"query": "PCD?", "doc_id": "doc1"}],
        )

        assert len(results) == 1
        assert results[0]["run_name"] == "run_1_qdrant_linear"
        assert results[0]["metrics"]["ndcg_at_10"] == 0.85
