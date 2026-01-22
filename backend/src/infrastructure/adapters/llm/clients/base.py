"""
Base LLM Client protocol and response models.

Defines the common interface for all LLM clients.
Clients are low-level abstractions over provider APIs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True)
class LLMMessage:
    """
    A single message in a conversation.

    Immutable value object for LLM API calls.
    """

    role: str
    content: str


@dataclass(frozen=True)
class LLMResponse:
    """
    Response from an LLM API call.

    Contains the generated content.
    """

    content: str
    model: str | None = None
    raw_response: Any = field(default=None, repr=False)


@runtime_checkable
class LLMClientProtocol(Protocol):
    """
    Protocol defining the interface all LLM clients must implement.

    Clients handle low-level API communication.
    """

    provider_id: str

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON-formatted output.

        Returns:
            LLMResponse with generated content.

        Raises:
            LLMConnectionError: If connection to provider fails.
            LLMResponseError: If provider returns invalid response.
        """
        ...

    async def complete_stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming completion, yielding tokens as they arrive.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.

        Yields:
            Token strings as they are generated.

        Raises:
            LLMConnectionError: If connection to provider fails.
            LLMResponseError: If provider returns invalid response.
        """
        yield ""  # pragma: no cover
        ...


class BaseLLMClient(ABC):
    """
    Abstract base class for LLM clients.

    Provides common functionality and enforces interface.
    """

    provider_id: str
    model: str

    def __init__(self, model: str) -> None:
        """
        Initialize the client with a model.

        Args:
            model: The model identifier to use.
        """
        self.model = model

    @abstractmethod
    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Generate a completion from the LLM."""
        ...

    @abstractmethod
    async def complete_stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion."""
        yield ""  # pragma: no cover
        ...
