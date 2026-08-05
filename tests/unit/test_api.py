"""
Unit tests for FastAPI REST Service endpoints (query, evaluate, feedback).
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from rag_eval.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_query_endpoint():
    payload = {"query": "What is programmed cell death?", "pipeline_type": "linear"}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "mitochondria" in data["answer"].lower()
    assert len(data["retrieved_contexts"]) > 0


def test_query_endpoint_empty():
    response = client.post("/query", json={"query": "   "})
    assert response.status_code == 400


@patch("rag_eval.api.main.MLflowTracker")
def test_evaluate_endpoint(mock_tracker_class):
    mock_tracker = MagicMock()
    mock_run = MagicMock()
    mock_run.info.run_id = "test-run-123"
    mock_tracker.start_run.return_value.__enter__.return_value = mock_run
    mock_tracker_class.return_value = mock_tracker

    payload = {
        "pipeline_name": "agentic_rag",
        "test_cases": [{"query": "PCD?", "doc_id": "pubmed_1"}],
    }
    response = client.post("/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["run_id"] == "test-run-123"
    assert data["metrics"]["ndcg_at_10"] == 0.885


@patch("rag_eval.api.main.MLflowTracker")
def test_feedback_endpoint(mock_tracker_class):
    mock_tracker = MagicMock()
    mock_tracker_class.return_value = mock_tracker

    payload = {
        "run_id": "test-run-123",
        "rating": 5,
        "comments": "Accurate clinical answer.",
    }
    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["rating"] == 5
