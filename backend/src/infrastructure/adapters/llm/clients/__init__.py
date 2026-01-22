"""
LLM Clients - Low-level reusable client implementations.

These clients provide a common interface for interacting with LLM providers.
They are used by higher-level adapters (ConversationPartner, FeedbackProvider, etc.).
"""

from src.infrastructure.adapters.llm.clients.anthropic_client import AnthropicClient
from src.infrastructure.adapters.llm.clients.base import (
    BaseLLMClient,
    LLMClientProtocol,
    LLMResponse,
)
from src.infrastructure.adapters.llm.clients.ollama_client import OllamaClient
from src.infrastructure.adapters.llm.clients.openai_client import OpenAIClient

__all__ = [
    "BaseLLMClient",
    "LLMClientProtocol",
    "LLMResponse",
    "AnthropicClient",
    "OllamaClient",
    "OpenAIClient",
]
