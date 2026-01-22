"""
LLM Provider data models.

Contains value objects and protocols for the unified provider system.
Pure data structures with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.infrastructure.adapters.llm.clients.base import BaseLLMClient
    from src.infrastructure.config.settings import Settings


class ModelCapability(Enum):
    """
    Capabilities that a model can have.

    Used to filter models for specific use cases.
    """

    CHAT = auto()  # General conversation (ConversationPartner)
    FEEDBACK = auto()  # Language feedback analysis (FeedbackProvider)
    SUMMARY = auto()  # Conversation summarization (SummaryProvider)
    JSON_MODE = auto()  # Supports structured JSON output


class ModelTier(Enum):
    """
    Model tier/quality level for UI display.

    Used to show badges like "Rapide", "Pro", "Standard" in the UI.
    """

    FAST = "fast"  # Fast/cheap models (gpt-4o-mini, claude-haiku)
    PRO = "pro"  # High-quality models (gpt-4o, claude-sonnet)
    STANDARD = "standard"  # Default tier


@dataclass(frozen=True)
class ModelInfo:
    """
    Information about an available LLM model.

    Used by the UI to display available models to the user.
    Includes capabilities for filtering by use case.

    Attributes:
        id: Full model ID in format "provider/model-name" (e.g., "openai/gpt-4o").
        name: Display name for UI (e.g., "GPT-4o").
        provider: Provider identifier (e.g., "openai").
        tier: Quality tier for UI badge (FAST, PRO, STANDARD).
        local: True for locally-running models (Ollama).
        capabilities: Set of capabilities this model supports.
        recommended_for: Primary recommended use case (for UI hints).
    """

    id: str
    name: str
    provider: str
    tier: ModelTier = ModelTier.STANDARD
    local: bool = False
    capabilities: frozenset[ModelCapability] = field(
        default_factory=lambda: frozenset(
            {ModelCapability.CHAT, ModelCapability.FEEDBACK, ModelCapability.SUMMARY}
        )
    )
    recommended_for: ModelCapability | None = None

    def supports(self, capability: ModelCapability) -> bool:
        """Check if this model supports a specific capability."""
        return capability in self.capabilities


# Backwards compatibility alias
FeedbackModelInfo = ModelInfo


class ProviderProtocol(Protocol):
    """
    Protocol that all LLM providers must implement.

    Providers register themselves using the @register_provider decorator.
    Each provider handles:
    - Availability checking (API key configured?)
    - Model listing (what models does this provider offer?)
    - Client creation (instantiate the LLM client)
    """

    provider_id: str
    provider_name: str

    @staticmethod
    def is_available(settings: Settings) -> bool:
        """
        Check if this provider is configured and available.

        Args:
            settings: Application settings with API keys.

        Returns:
            True if provider can be used (has required API key).
        """
        ...

    @staticmethod
    def list_models() -> list[ModelInfo]:
        """
        List all models this provider offers.

        Returns:
            List of ModelInfo for each available model.
        """
        ...

    @staticmethod
    def create_client(model: str, settings: Settings) -> BaseLLMClient:
        """
        Create an LLM client for a specific model.

        Args:
            model: Model name (without provider prefix).
            settings: Application settings for API keys.

        Returns:
            Configured ConversationPartner instance.
        """
        ...
