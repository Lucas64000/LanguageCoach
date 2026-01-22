"""
LLM Adapters package.

Provides unified LLM provider registry for dynamic model selection.
Supports multiple use cases: chat, feedback, summary.

Architecture:
- clients/: Low-level LLM API clients (OpenAI, Anthropic, Ollama, etc.)
- providers/: Provider registration (models, availability)
- services/: High-level port implementations (ConversationPartner, etc.)
"""

# High-level services (port implementations)
from src.infrastructure.adapters.llm.services import (
    LLMConversationPartner,
    LLMFeedbackAnalyzer,
    LLMSummaryGenerator,
)

# Low-level clients
from src.infrastructure.adapters.llm.clients import (
    AnthropicClient,
    BaseLLMClient,
    LLMClientProtocol,
    LLMResponse,
    OllamaClient,
    OpenAIClient,
)
from src.infrastructure.adapters.llm.models import (
    FeedbackModelInfo,
    ModelCapability,
    ModelInfo,
    ModelTier,
    ProviderProtocol,
)
from src.infrastructure.adapters.llm.registry import (
    register_provider,
    registry,
)

__all__ = [
    # Models
    "ModelCapability",
    "ModelInfo",
    "ModelTier",
    "FeedbackModelInfo",
    "ProviderProtocol",
    # Registry
    "register_provider",
    "registry",
    # Clients
    "BaseLLMClient",
    "LLMClientProtocol",
    "LLMResponse",
    "AnthropicClient",
    "OllamaClient",
    "OpenAIClient",
    # Adapters
    "LLMConversationPartner",
    "LLMFeedbackAnalyzer",
    "LLMSummaryGenerator",
]
