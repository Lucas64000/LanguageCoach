"""
OpenAI LLM Client - Low-level client for OpenAI API.

Provides reusable client for any adapter needing OpenAI completions.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from openai import AsyncOpenAI

from src.core.exceptions import PartnerConnectionError, PartnerResponseError
from src.infrastructure.adapters.llm.clients.base import (
    BaseLLMClient,
    LLMMessage,
    LLMResponse,
)

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletion


class OpenAIClient(BaseLLMClient):
    """
    OpenAI API client.

    Handles all OpenAI API communication with proper error handling.
    Reusable across different services (ConversationPartner, FeedbackProvider, etc.).
    """

    provider_id = "openai"

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        client: AsyncOpenAI | None = None,
    ) -> None:
        """
        Initialize the OpenAI client.

        Args:
            api_key: OpenAI API key.
            model: Model to use for completions.
            client: Optional pre-configured client (for testing).
        """
        super().__init__(model)
        self._client = client or AsyncOpenAI(api_key=api_key)

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Generate a completion using OpenAI API.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON-formatted output.

        Returns:
            LLMResponse with content.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
            }

            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response: ChatCompletion = await self._client.chat.completions.create(
                **kwargs
            )

            content = response.choices[0].message.content or ""

            return LLMResponse(
                content=content,
                model=self.model,
                raw_response=response,
            )

        # Exceptions à définir plus tard
        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise PartnerConnectionError(
                    f"Cannot connect to OpenAI API: {e}"
                ) from e
            raise PartnerResponseError(f"OpenAI API error: {e}") from e

    async def complete_stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming completion using OpenAI API.

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
        openai_messages = [{"role": m.role, "content": m.content} for m in messages]

        try:
            kwargs: dict[str, Any] = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            stream = await self._client.chat.completions.create(**kwargs)

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                raise PartnerConnectionError(
                    f"Cannot connect to OpenAI API: {e}"
                ) from e
            raise PartnerResponseError(f"OpenAI API error: {e}") from e
