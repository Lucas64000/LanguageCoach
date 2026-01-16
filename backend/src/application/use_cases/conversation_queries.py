"""
Conversation Query Use Cases.

Read-only operations for retrieving conversations.
"""

from uuid import UUID

from src.application.dtos import (
    ConversationDetailOutput,
    ConversationOutput,
)
from src.application.mappers import ConversationMapper
from src.core.ports import ConversationRepository
from src.core.value_objects import ConversationStatus


class ConversationQueries:
    """
    Query use cases for conversations.

    Groups read-only operations that retrieve conversation data.
    """

    def __init__(self, repository: ConversationRepository) -> None:
        """
        Initialize with repository dependency.

        Args:
            repository: Port for conversation retrieval.
        """
        self._repository = repository

    async def get(self, conversation_id: UUID) -> ConversationDetailOutput:
        """
        Get a conversation with all its messages.

        Args:
            conversation_id: The unique identifier of the conversation.

        Returns:
            Detailed conversation DTO with all messages.

        Raises:
            ConversationNotFoundError: If no conversation with this ID exists.
        """
        conversation = await self._repository.get(conversation_id)
        return ConversationMapper.to_detail_output(conversation)

    async def list_all(self) -> list[ConversationOutput]:
        """
        List all conversations.

        Returns:
            List of conversation summary DTOs.
        """
        conversations = await self._repository.list_all()
        return [ConversationMapper.to_output(c) for c in conversations]

    async def list_by_status(
        self, status: ConversationStatus
    ) -> list[ConversationOutput]:
        """
        List conversations filtered by status.

        Args:
            status: The status to filter by.

        Returns:
            List of conversation summary DTOs with the given status.
        """
        conversations = await self._repository.list_by_status(status)
        return [ConversationMapper.to_output(c) for c in conversations]

