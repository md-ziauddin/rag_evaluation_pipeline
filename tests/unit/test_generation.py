"""
Unit tests for Milestone 6 (M6) Generation, Orchestration, and FastAPI Service.

Tests GroqLLMProvider, BedrockLLMProvider, LinearRAGPipeline, AgenticRAGGraph,
and FastAPI REST endpoints.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from rag_eval.api.main import app
from rag_eval.chunking.schemas import Chunk
from rag_eval.generation.bedrock import BedrockLLMProvider
from rag_eval.generation.groq_provider import GroqLLMProvider
from rag_eval.orchestration.agentic import AgenticRAGGraph
from rag_eval.orchestration.linear import LinearRAGPipeline


class TestLLMProviders:
    """Tests for Groq and Bedrock LLM providers."""

    @patch("rag_eval.generation.groq_provider.Groq")
    def test_groq_llm_provider_generate(self, mock_groq_class):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Groq clinical answer"
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client

        provider = GroqLLMProvider(api_key="mock-key", model_name="llama-3.3-70b-versatile")
        output = provider.generate("Medical question", system_prompt="System instructions")

        assert output == "Groq clinical answer"
        mock_client.chat.completions.create.assert_called_once()

    @patch("boto3.client")
    def test_bedrock_llm_provider_generate(self, mock_boto):
        mock_bedrock = MagicMock()
        mock_bedrock.converse.return_value = {
            "output": {"message": {"content": [{"text": "Bedrock clinical answer"}]}}
        }
        mock_boto.return_value = mock_bedrock

        provider = BedrockLLMProvider(model_name="anthropic.claude-3-sonnet-20240229-v1:0")
        output = provider.generate("Medical question", system_prompt="System instructions")

        assert output == "Bedrock clinical answer"
        mock_bedrock.converse.assert_called_once()


class TestOrchestrationPipelines:
    """Tests for LinearRAGPipeline and AgenticRAGGraph."""

    def test_linear_rag_pipeline(self):
        mock_retriever = MagicMock()
        chunk = Chunk(
            chunk_id="c1", doc_id="d1", chunk_index=0, text="Medical text context", token_count=3
        )
        mock_retriever.retrieve.return_value = [chunk]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Generated response"

        pipeline = LinearRAGPipeline(retriever=mock_retriever, llm_provider=mock_llm)
        result = pipeline.run(query="What is the treatment?")

        assert result["answer"] == "Generated response"
        assert result["pipeline_type"] == "linear"
        assert len(result["retrieved_chunks"]) == 1

    def test_agentic_rag_graph(self):
        mock_retriever = MagicMock()
        chunk = Chunk(
            chunk_id="c1", doc_id="d1", chunk_index=0, text="Medical text context", token_count=3
        )
        mock_retriever.retrieve.return_value = [chunk]

        mock_llm = MagicMock()
        mock_llm.generate.return_value = "Agentic answer"

        graph = AgenticRAGGraph(retriever=mock_retriever, llm_provider=mock_llm)
        result = graph.run(query="medical question")

        assert result["answer"] == "Agentic answer"
        assert result["pipeline_type"] == "agentic"


class TestFastAPIEndpoints:
    """Tests for FastAPI endpoints."""

    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_query_endpoint(self):
        client = TestClient(app)
        response = client.post("/query", json={"query": "What is PCD?", "pipeline_type": "linear"})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
