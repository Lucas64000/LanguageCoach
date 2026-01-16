"""
Conversation Lifecycle Use Cases.

Simple state transitions for conversations: archive, restore, end, delete.
"""

from uuid import UUID

from src.application.dtos import ConversationStatusOutput
from src.application.mappers import ConversationMapper
from src.core.ports import ConversationRepository


class ChangeConversationStatus:
    """
    Use cases for conversation lifecycle state transitions.

    Groups simple CRUD-like operations that follow the same pattern:
    load → mutate → save → return DTO.
    """

    def __init__(self, repository: ConversationRepository) -> None:
        """
        Initialize with repository dependency.

        Args:
            repository: Port for conversation persistence.
        """
        self._repository = repository

    async def archive(self, conversation_id: UUID) -> ConversationStatusOutput:
        """
        Archive a conversation.

        Args:
            conversation_id: ID of the conversation to archive.

        Returns:
            DTO with conversation ID and new status.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
            InvalidConversationStateError: If already archived.
        """
        conversation = await self._repository.get(conversation_id)
        conversation.archive()
        await self._repository.save(conversation)
        return ConversationMapper.to_status_output(conversation)

    async def restore(self, conversation_id: UUID) -> ConversationStatusOutput:
        """
        Restore an archived conversation.

        Args:
            conversation_id: ID of the conversation to restore.

        Returns:
            DTO with conversation ID and new status.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
            InvalidConversationStateError: If not archived.
        """
        conversation = await self._repository.get(conversation_id)
        conversation.restore()
        await self._repository.save(conversation)
        return ConversationMapper.to_status_output(conversation)

    async def end(self, conversation_id: UUID) -> ConversationStatusOutput:
        """
        Mark a conversation as completed.

        Args:
            conversation_id: ID of the conversation to end.

        Returns:
            DTO with conversation ID and new status.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
        """
        conversation = await self._repository.get(conversation_id)
        conversation.end()
        await self._repository.save(conversation)
        return ConversationMapper.to_status_output(conversation)

    async def delete(self, conversation_id: UUID) -> bool:
        """
        Permanently delete a conversation.

        Args:
            conversation_id: ID of the conversation to delete.

        Returns:
            True if deleted successfully.
        """
        # No need to validate existence
        await self._repository.delete(conversation_id)
        return True

