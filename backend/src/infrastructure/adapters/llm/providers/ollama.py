"""
Ollama Provider - registered via decorator.

Provides local LLM models (no API key required).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.infrastructure.adapters.llm.clients.ollama_client import OllamaClient
from src.infrastructure.adapters.llm.models import ModelCapability, ModelInfo, ModelTier
from src.infrastructure.adapters.llm.registry import register_provider

if TYPE_CHECKING:
    from src.infrastructure.config.settings import Settings


@register_provider
class OllamaProvider:
    """Ollama provider - local LLM models (no API key required)."""

    provider_id = "ollama"
    provider_name = "Ollama (Local)"

    @staticmethod
    def is_available(settings: Settings) -> bool:
        """Ollama is always available (local server)."""
        return True

    @staticmethod
    def list_models() -> list[ModelInfo]:
        """
        List available Ollama models with capabilities.

        Note: Could be enhanced to query Ollama /api/tags for installed models.
        Currently returns common defaults.
        """
        chat_capabilities = frozenset(
            {
                ModelCapability.CHAT,
                ModelCapability.FEEDBACK,
                ModelCapability.SUMMARY,
            }
        )

        return [
            ModelInfo(
                id="ollama/llama3.2",
                name="Llama 3.2",
                provider="ollama",
                tier=ModelTier.FAST,
                local=True,
                capabilities=chat_capabilities,
                recommended_for=ModelCapability.CHAT,
            ),
            ModelInfo(
                id="ollama/gemma2.5:7b",
                name="Gemma 2.5 7B",
                provider="ollama",
                tier=ModelTier.FAST,
                local=True,
                capabilities=chat_capabilities,
            ),
        ]

    @staticmethod
    def create_client(model: str, settings: Settings) -> OllamaClient:
        """Create an Ollama client for a specific model."""
        return OllamaClient(
            model=model,
            base_url=settings.ollama_base_url,
            timeout=settings.ollama_request_timeout,
        )
