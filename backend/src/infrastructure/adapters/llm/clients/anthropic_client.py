"""
Anthropic LLM Client - Low-level client for Anthropic Claude API.

Provides reusable client for any adapter needing Anthropic completions.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from anthropic import AsyncAnthropic

from src.core.exceptions import PartnerConnectionError, PartnerResponseError
from src.infrastructure.adapters.llm.clients.base import (
    BaseLLMClient,
    LLMMessage,
    LLMResponse,
)

if TYPE_CHECKING:
    from anthropic.types import Message as AnthropicMessage


class AnthropicClient(BaseLLMClient):
    """
    Anthropic API client.

    Handles all Anthropic API communication with proper error handling.
    Reusable across different services (ConversationPartner, FeedbackProvider, etc.).
    """

    provider_id = "anthropic"
    DEFAULT_MAX_TOKENS = 1024

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-haiku-20240307",
        client: AsyncAnthropic | None = None,
    ) -> None:
        """
        Initialize the Anthropic client.

        Args:
            api_key: Anthropic API key.
            model: Model to use for completions.
            client: Optional pre-configured client (for testing).
        """
        super().__init__(model)
        self._client = client or AsyncAnthropic(api_key=api_key)

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Generate a completion using Anthropic API.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON-formatted output (via system prompt).

        Returns:
            LLMResponse with content.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        # Separate system message from conversation
        system_content = ""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                anthropic_messages.append({"role": msg.role, "content": msg.content})

        # Add JSON instruction to system prompt if json_mode
        if json_mode and system_content:
            system_content += "\n\nIMPORTANT: Respond with valid JSON only."
        elif json_mode:
            system_content = "Respond with valid JSON only."

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens or self.DEFAULT_MAX_TOKENS,
                "temperature": temperature,
            }

            if system_content:
                kwargs["system"] = system_content

            response: AnthropicMessage = await self._client.messages.create(**kwargs)

            # Extract text content
            content = ""
            if response.content and len(response.content) > 0:
                content = response.content[0].text

            return LLMResponse(
                content=content,
                model=self.model,
                raw_response=response,
            )

        # Exceptions à définir plus tard
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise PartnerConnectionError(
                    f"Cannot connect to Anthropic API: {e}"
                ) from e
            raise PartnerResponseError(f"Anthropic API error: {e}") from e

    async def complete_stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming completion using Anthropic API.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Yields:
            Token strings as they arrive.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        # Separate system message from conversation
        system_content = ""
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_content = msg.content
            else:
                anthropic_messages.append({"role": msg.role, "content": msg.content})

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens or self.DEFAULT_MAX_TOKENS,
                "temperature": temperature,
            }

            if system_content:
                kwargs["system"] = system_content

            async with self._client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise PartnerConnectionError(
                    f"Cannot connect to Anthropic API: {e}"
                ) from e
            raise PartnerResponseError(f"Anthropic API error: {e}") from e
