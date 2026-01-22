"""
LLM Conversation Partner adapter.

Implements the ConversationPartner port using LLM clients.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from src.core.entities.message import Message, MessageRole
from src.core.value_objects import ConversationTone
from src.infrastructure.adapters.llm.clients.base import BaseLLMClient, LLMMessage
from src.infrastructure.prompts import build_coach_system_prompt

if TYPE_CHECKING:
    pass


class LLMConversationPartner:
    """
    ConversationPartner implementation using LLM clients.

    Wraps any LLM client to provide conversation responses.
    Implements the ConversationPartner protocol from core.ports.
    """

    def __init__(self, client: BaseLLMClient) -> None:
        """
        Initialize with an LLM client.

        Args:
            client: The LLM client to use for generation.
        """
        self._client = client

    @property
    def model(self) -> str:
        """Get the model name (for backwards compatibility)."""
        return self._client.model

    def _build_messages(
        self,
        context: str,
        messages: list[Message],
        tone: ConversationTone | None = None,
    ) -> list[LLMMessage]:
        """
        Build LLM messages from conversation history.

        Args:
            context: The conversation topic/scenario.
            messages: The message history.
            tone: The coaching tone/style.

        Returns:
            List of LLMMessage for the API call.
        """
        system_prompt = build_coach_system_prompt(context, tone)
        llm_messages = [LLMMessage(role="system", content=system_prompt)]

        for msg in messages:
            role = "assistant" if msg.role == MessageRole.COACH else "user"
            llm_messages.append(LLMMessage(role=role, content=msg.content))

        return llm_messages

    async def generate_response(
        self,
        context: str,
        messages: list[Message],
        tone: ConversationTone | None = None,
    ) -> str:
        """
        Generate a response based on conversation context and history.

        Args:
            context: The conversation topic/scenario (e.g., "coffee shop").
            messages: The message history for context.
            tone: The coaching tone/style.

        Returns:
            The generated response text.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        llm_messages = self._build_messages(context, messages, tone)
        response = await self._client.complete(llm_messages)
        return response.content

    async def generate_response_stream(
        self,
        context: str,
        messages: list[Message],
        tone: ConversationTone | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming response, yielding tokens as they arrive.

        Args:
            context: The conversation topic/scenario.
            messages: The message history for context.
            tone: The coaching tone/style.

        Yields:
            Token strings as they are generated.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        llm_messages = self._build_messages(context, messages, tone)
        async for token in self._client.complete_stream(llm_messages):
            yield token
