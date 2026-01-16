"""
ConversationPartner port for coach interactions.

Port defines the contract for generating responses.
Core layer must have ZERO external imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, Protocol

from src.core.entities.message import Message

if TYPE_CHECKING:
    from src.core.value_objects import ConversationTone


class ConversationPartner(Protocol):
    """
    Port for coach response generation.

    Implementations must be in infrastructure layer.
    """

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
        """
        ...

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
        """
        yield ""  # type: ignore  # pragma: no cover
        ...
