"""
Linear RAG Pipeline Implementation (M6).

Baseline control flow executing deterministic Retrieve -> Rerank -> Generate sequence.
"""

from typing import Any

from rag_eval.generation.base import BaseLLMProvider
from rag_eval.generation.prompts import MEDICAL_QA_SYSTEM_PROMPT, MEDICAL_QA_USER_PROMPT
from rag_eval.retrieval.base import BaseReranker, BaseRetriever


class LinearRAGPipeline:
    """
    Linear RAG pipeline for baseline retrieval and answer generation.
    """

    def __init__(
        self,
        retriever: BaseRetriever,
        llm_provider: BaseLLMProvider,
        reranker: BaseReranker | None = None,
    ):
        self.retriever = retriever
        self.llm_provider = llm_provider
        self.reranker = reranker

    def run(self, query: str, top_k: int = 10, top_n: int = 5) -> dict[str, Any]:
        """Execute linear Retrieve -> Rerank -> Generate pipeline."""
        # 1. Retrieve candidates
        candidate_chunks = self.retriever.retrieve(query, top_k=top_k)

        # 2. Rerank if reranker is provided
        if self.reranker and candidate_chunks:
            final_chunks = self.reranker.rerank(query, candidate_chunks, top_n=top_n)
        else:
            final_chunks = candidate_chunks[:top_n]

        # 3. Format context string
        context_str = "\n\n".join([f"[{i + 1}] {c.text}" for i, c in enumerate(final_chunks)])

        # 4. Generate answer via LLM Provider
        user_prompt = MEDICAL_QA_USER_PROMPT.format(context=context_str, query=query)
        answer = self.llm_provider.generate(
            prompt=user_prompt,
            system_prompt=MEDICAL_QA_SYSTEM_PROMPT,
        )

        return {
            "query": query,
            "answer": answer,
            "retrieved_chunks": final_chunks,
            "pipeline_type": "linear",
        }
