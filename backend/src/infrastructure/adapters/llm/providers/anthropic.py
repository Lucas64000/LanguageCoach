"""
Anthropic Provider - registered via decorator.

Provides Claude models for all use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.infrastructure.adapters.llm.clients.anthropic_client import AnthropicClient
from src.infrastructure.adapters.llm.models import ModelCapability, ModelInfo, ModelTier
from src.infrastructure.adapters.llm.registry import register_provider

if TYPE_CHECKING:
    from src.infrastructure.config.settings import Settings


@register_provider
class AnthropicProvider:
    """Anthropic provider - Claude models for all use cases."""

    provider_id = "anthropic"
    provider_name = "Anthropic"

    @staticmethod
    def is_available(settings: Settings) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(settings.anthropic_api_key)

    @staticmethod
    def list_models() -> list[ModelInfo]:
        """List available Anthropic models with capabilities."""
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
                id="anthropic/claude-sonnet-4-20250514",
                name="Claude Sonnet 4",
                provider="anthropic",
                tier=ModelTier.PRO,
                local=False,
                capabilities=all_capabilities,
                recommended_for=ModelCapability.CHAT,
            ),
            ModelInfo(
                id="anthropic/claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                provider="anthropic",
                tier=ModelTier.FAST,
                local=False,
                capabilities=all_capabilities,
                recommended_for=ModelCapability.FEEDBACK,
            ),
        ]

    @staticmethod
    def create_client(model: str, settings: Settings) -> AnthropicClient:
        """Create an Anthropic client for a specific model."""
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic models")
        return AnthropicClient(api_key=settings.anthropic_api_key, model=model)
