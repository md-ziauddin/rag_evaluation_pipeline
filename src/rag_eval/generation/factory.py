"""
Factory for Instantiating and Resolving LLM Providers.

Implements prioritized resolution:
1. AWS Bedrock (primary default)
2. Groq API (high-speed fallback if AWS credentials unavailable)
3. Intuitive error without exposing technical details if neither is configured.
"""

import logging
import os

import boto3

from rag_eval.config.settings import settings
from rag_eval.generation.base import BaseLLMProvider
from rag_eval.generation.bedrock import BedrockLLMProvider
from rag_eval.generation.groq_provider import GroqLLMProvider

logger = logging.getLogger(__name__)


class ResilientLLMProvider(BaseLLMProvider):
    """
    Resilient LLM Provider that executes requests against AWS Bedrock first,
    falling back to Groq API on failure or credential unavailability, and
    providing user-friendly errors without exposing internal technical details.
    """

    def __init__(
        self,
        primary_provider: BaseLLMProvider | None = None,
        fallback_provider: BaseLLMProvider | None = None,
    ):
        model_name = "resilient-llm"
        if primary_provider:
            model_name = primary_provider.model_name
        elif fallback_provider:
            model_name = fallback_provider.model_name
        super().__init__(model_name=model_name)
        self.primary_provider = primary_provider
        self.fallback_provider = fallback_provider

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        # Try primary (Bedrock)
        if self.primary_provider is not None:
            try:
                return self.primary_provider.generate(prompt=prompt, system_prompt=system_prompt)
            except Exception as e:
                logger.warning(
                    "Primary LLM provider (%s) execution failed: %s. Attempting fallback.",
                    self.primary_provider.__class__.__name__,
                    e,
                )

        # Fallback to secondary (Groq)
        if self.fallback_provider is not None:
            try:
                return self.fallback_provider.generate(prompt=prompt, system_prompt=system_prompt)
            except Exception as e:
                logger.error(
                    "Fallback LLM provider (%s) execution failed: %s.",
                    self.fallback_provider.__class__.__name__,
                    e,
                )

        raise RuntimeError(
            "Language model generation is currently unavailable. "
            "Please ensure AWS Bedrock credentials or a valid GROQ_API_KEY is configured."
        )


class LLMFactory:
    """
    Factory class creating LLMProvider instances with automatic Bedrock -> Groq fallback.
    """

    @staticmethod
    def is_bedrock_configured() -> bool:
        """Check if AWS credentials exist in environment or config without exposing details."""
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            return True
        if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
            return True
        try:
            session = boto3.Session(region_name=settings.AWS_REGION)
            creds = session.get_credentials()
            return creds is not None and bool(creds.access_key)
        except Exception:
            return False

    @staticmethod
    def is_groq_configured() -> bool:
        """Check if Groq API key is present."""
        return bool(settings.GROQ_API_KEY or os.environ.get("GROQ_API_KEY"))

    @classmethod
    def get_provider(
        cls,
        provider_type: str | None = None,
        model_name: str | None = None,
    ) -> BaseLLMProvider:
        """
        Creates and returns an LLM provider.
        If provider_type is explicitly specified ('bedrock' or 'groq'), returns that provider.
        Otherwise, resolves with Bedrock > Groq > Intuitive error.
        """
        if provider_type is not None:
            requested = provider_type.lower().strip()
            if requested == "bedrock":
                if not cls.is_bedrock_configured():
                    if cls.is_groq_configured():
                        logger.info(
                            "Bedrock requested but AWS credentials not configured. "
                            "Falling back to Groq."
                        )
                        return GroqLLMProvider(model_name=model_name)
                    raise RuntimeError(
                        "Language model service is currently unavailable: AWS Bedrock credentials "
                        "are not configured, and no Groq fallback key is available."
                    )
                return BedrockLLMProvider(model_name=model_name or settings.BEDROCK_LLM_MODEL_ID)

            if requested == "groq":
                if not cls.is_groq_configured():
                    if cls.is_bedrock_configured():
                        logger.info(
                            "Groq requested but GROQ_API_KEY not configured. "
                            "Falling back to Bedrock."
                        )
                        return BedrockLLMProvider(
                            model_name=model_name or settings.BEDROCK_LLM_MODEL_ID
                        )
                    raise RuntimeError(
                        "Language model service is currently unavailable: GROQ_API_KEY is not "
                        "configured, and no Bedrock credentials are available."
                    )
                return GroqLLMProvider(model_name=model_name or settings.GROQ_MODEL_ID)

        # Default resolution: Bedrock > Groq
        primary: BaseLLMProvider | None = None
        fallback: BaseLLMProvider | None = None

        if cls.is_bedrock_configured():
            try:
                primary = BedrockLLMProvider(model_name=model_name or settings.BEDROCK_LLM_MODEL_ID)
            except Exception as e:
                logger.warning("Failed to initialize Bedrock LLM: %s", e)

        if cls.is_groq_configured():
            try:
                fallback = GroqLLMProvider(model_name=model_name or settings.GROQ_MODEL_ID)
            except Exception as e:
                logger.warning("Failed to initialize Groq LLM: %s", e)

        if primary is None and fallback is None:
            raise RuntimeError(
                "Language model service is currently unavailable. "
                "Please configure AWS Bedrock credentials or set a valid GROQ_API_KEY to generate "
                "clinical answers."
            )

        if primary is not None and fallback is not None:
            return ResilientLLMProvider(primary_provider=primary, fallback_provider=fallback)
        if primary is not None:
            return primary
        if fallback is not None:
            return fallback

        raise RuntimeError(
            "Language model service is currently unavailable. "
            "Please configure AWS Bedrock credentials or set a valid GROQ_API_KEY to generate "
            "clinical answers."
        )
