"""
Groq LLM Provider Implementation.

Uses official Groq SDK for ultra-high speed Llama 3.3 / Mixtral inference.
"""

import os
from typing import Any

from groq import Groq

from rag_eval.config.settings import settings
from rag_eval.generation.base import BaseLLMProvider


class GroqLLMProvider(BaseLLMProvider):
    """
    Groq API LLM provider supporting Llama 3.3 70B, Llama 3 8B, and Mixtral.
    """

    def __init__(
        self,
        model_name: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ):
        model = model_name or settings.GROQ_MODEL_ID or "llama-3.3-70b-versatile"
        super().__init__(model_name=model, max_tokens=max_tokens, temperature=temperature)

        self.api_key = api_key or settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY is missing! Set GROQ_API_KEY in your environment or .env file."
            )

        self.client = Groq(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        """Execute chat completion request via Groq API."""
        messages: list[Any] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""
