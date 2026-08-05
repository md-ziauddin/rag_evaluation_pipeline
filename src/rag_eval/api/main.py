"""
FastAPI Production REST Service.
"""

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_eval.config.settings import settings

app = FastAPI(
    title="Medical RAG Evaluation API",
    version="1.0.0",
    description="Production Medical RAG pipeline REST service supporting Linear and Agentic RAG.",
)


class HealthResponse(BaseModel):
    status: str
    environment: str


class QueryRequest(BaseModel):
    query: str = Field(..., description="User medical question")
    pipeline_type: str = Field(
        default="linear", description="Pipeline type ('linear' or 'agentic')"
    )


@app.get("/health", response_model=HealthResponse)
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.ENV}


@app.post("/query")
def query_pipeline(request: QueryRequest) -> dict[str, Any]:
    """Query end-to-end medical RAG pipeline."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")

    return {
        "status": "success",
        "query": request.query,
        "pipeline_type": request.pipeline_type,
        "message": "Endpoint ready for pipeline execution.",
    }
