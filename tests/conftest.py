"""
Pytest configuration and global test fixtures.
"""

import os

import pytest

# Ensure tests run with hermetic, fast SQLite in-memory tracking and test environment
os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///:memory:"
os.environ["ENV"] = "test"


class MockEmbeddingProvider:
    """Fast, deterministic in-memory mock embedding provider for tests."""

    def __init__(self, dimension: int = 1024):
        self.dimension = dimension
        self.model_name = "mock-embedding-model"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Deterministic normalized vectors
        vectors = []
        for text in texts:
            val = float(len(text) % 10 + 1) / 10.0
            vec = [val] * self.dimension
            vectors.append(vec)
        return vectors

    def embed_query(self, text: str) -> list[float]:
        val = float(len(text) % 10 + 1) / 10.0
        return [val] * self.dimension


class MockLLMProvider:
    """Fast, deterministic in-memory mock LLM provider for tests."""

    def __init__(self, model_name: str = "mock-llm"):
        self.model_name = model_name

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        if "rewrite" in (system_prompt or "").lower():
            return "What is the biological role of mitochondria in programmed cell death?"
        return "Mitochondria play a key role in programmed cell death."


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider(dimension=1024)


@pytest.fixture
def mock_llm_provider() -> MockLLMProvider:
    return MockLLMProvider()
