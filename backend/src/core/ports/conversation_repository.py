"""
Repository ports for conversation domain.

Port defines the contract for persistence operations.
Core layer must have ZERO external imports.
"""

from typing import Protocol
from uuid import UUID

from src.core.entities.conversation import Conversation, ConversationStatus


class ConversationRepository(Protocol):
    """
    Port for conversation persistence operations.

    Implementations must be in infrastructure layer.
    """

    async def save(self, conversation: Conversation) -> None:
        """
        Persist a conversation.

        Args:
            conversation: The conversation entity to save.
        """
        ...

    async def find(self, id: UUID) -> Conversation | None:
        """
        Retrieve a conversation by ID.

        Args:
            id: The unique identifier of the conversation.

        Returns:
            The conversation if found, None otherwise.
        """
        ...

    async def get(self, id: UUID) -> Conversation:
        """
        Retrieve a conversation by ID or raise if not found.

        Args:
            id: The unique identifier of the conversation.

        Returns:
            The conversation.

        Raises:
            ConversationNotFoundError: If no conversation with this ID exists.
        """
        ...

    async def list_all(self) -> list[Conversation]:
        """
        Retrieve all conversations.

        Returns:
            List of all conversations.
        """
        ...

    async def list_by_status(self, status: ConversationStatus) -> list[Conversation]:
        """
        Retrieve conversations filtered by status.

        Args:
            status: The status to filter by.

        Returns:
            List of conversations with the given status.
        """
        ...

    async def delete(self, id: UUID) -> bool:
        """
        Delete a conversation by ID.

        Args:
            id: The unique identifier of the conversation.

        Returns:
            True if deleted, False if not found.
        """
        ...

    async def get_active(self, id: UUID) -> Conversation:
        """
        Retrieve an active conversation or raise if not available.

        Args:
            id: Conversation identifier.

        Returns:
            The active conversation.

        Raises:
            ConversationNotFoundError: If the conversation does not exist.
            InvalidConversationStateError: If the conversation is archived or completed.
        """
        ...

    async def get_by_message_id(self, message_id: UUID) -> Conversation:
        """
        Retrieve the conversation containing a specific message.

        Args:
            message_id: Identifier of the message.

        Returns:
            The conversation containing the message.
        """
        ...
