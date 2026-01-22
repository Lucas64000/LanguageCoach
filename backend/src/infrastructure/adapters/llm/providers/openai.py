"""
OpenAI Provider - registered via decorator.

Provides GPT models for all use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.infrastructure.adapters.llm.clients.openai_client import OpenAIClient
from src.infrastructure.adapters.llm.models import ModelCapability, ModelInfo, ModelTier
from src.infrastructure.adapters.llm.registry import register_provider

if TYPE_CHECKING:
    from src.infrastructure.config.settings import Settings


@register_provider
class OpenAIProvider:
    """OpenAI provider - GPT models for all use cases."""

    provider_id = "openai"
    provider_name = "OpenAI"

    @staticmethod
    def is_available(settings: Settings) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(settings.openai_api_key)

    @staticmethod
    def list_models() -> list[ModelInfo]:
        """List available OpenAI models with capabilities."""
        all_capabilities = frozenset(
            {
                ModelCapability.CHAT,
                ModelCapability.FEEDBACK,
                ModelCapability.SUMMARY,
                ModelCapability.JSON_MODE,
            }
        )

        return [
            ModelInfo(
                id="openai/gpt-4o",
                name="GPT-4o",
                provider="openai",
                tier=ModelTier.PRO,
                local=False,
                capabilities=all_capabilities,
                recommended_for=ModelCapability.CHAT,
            ),
            ModelInfo(
                id="openai/gpt-4o-mini",
                name="GPT-4o Mini",
                provider="openai",
                tier=ModelTier.FAST,
                local=False,
                capabilities=all_capabilities,
                recommended_for=ModelCapability.FEEDBACK,
            ),
            ModelInfo(
                id="openai/gpt-4-turbo",
                name="GPT-4 Turbo",
                provider="openai",
                tier=ModelTier.PRO,
                local=False,
                capabilities=all_capabilities,
            ),
        ]

    @staticmethod
    def create_client(model: str, settings: Settings) -> OpenAIClient:
        """Create an OpenAI client for a specific model."""
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI models")
        return OpenAIClient(api_key=settings.openai_api_key, model=model)
