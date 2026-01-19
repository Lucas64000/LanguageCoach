"""
SummaryProvider port for conversation summary generation.

Port defines the contract for generating end-of-session summaries.
Core layer must have ZERO external imports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.core.entities.conversation import Conversation
    from src.core.entities.conversation_summary import ConversationSummary


class SummaryProvider(Protocol):
    """
    Port for conversation summary generation.

    Implementations must be in infrastructure layer.
    """

    async def create_summary(self, conversation: Conversation) -> ConversationSummary:
        """
        Create an end-of-session summary for a conversation.

        Args:
            conversation: The completed conversation to summarize.

        Returns:
            ConversationSummary with fluency score and remarks.
        """
        ...
