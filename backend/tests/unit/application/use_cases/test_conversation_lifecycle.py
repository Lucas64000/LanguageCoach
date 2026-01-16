"""
Unit tests for ChangeConversationStatus use case.

Tests lifecycle operations: archive, restore, end, delete.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.conversation_lifecycle import ChangeConversationStatus
from src.core.entities.conversation import Conversation
from src.core.exceptions import ConversationNotFoundError, InvalidConversationStateError


class TestArchive:
    """Tests for ChangeConversationStatus.archive()."""

    async def test_archives_active_conversation(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """archive() sets status to archived."""
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)
        result = await use_case.archive(conversation.id)

        assert result.status == "archived"
        assert conversation.is_archived
        mock_repository.save.assert_called_once_with(conversation)

    async def test_raises_when_not_found(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """archive() raises ConversationNotFoundError for missing conversation."""
        fake_id = uuid4()
        mock_repository.get = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(ConversationNotFoundError):
            await use_case.archive(fake_id)

    async def test_raises_when_already_archived(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """archive() raises InvalidConversationStateError for archived conversation."""
        conversation.archive()  # Already archived
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(InvalidConversationStateError, match="already archived"):
            await use_case.archive(conversation.id)

    async def test_raises_when_completed(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """archive() raises InvalidConversationStateError for completed conversation."""
        conversation.end()  # Completed
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(InvalidConversationStateError, match="completed"):
            await use_case.archive(conversation.id)


class TestRestore:
    """Tests for ChangeConversationStatus.restore()."""

    async def test_restores_archived_conversation(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """restore() sets status back to active."""
        conversation.archive()  # First archive it
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)
        result = await use_case.restore(conversation.id)

        assert result.status == "active"
        assert conversation.is_active
        mock_repository.save.assert_called_once_with(conversation)

    async def test_raises_when_not_found(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """restore() raises ConversationNotFoundError for missing conversation."""
        fake_id = uuid4()
        mock_repository.get = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(ConversationNotFoundError):
            await use_case.restore(fake_id)

    async def test_raises_when_already_active(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """restore() raises InvalidConversationStateError for active conversation."""
        # conversation is already active by default
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(InvalidConversationStateError, match="already active"):
            await use_case.restore(conversation.id)


class TestEnd:
    """Tests for ChangeConversationStatus.end()."""

    async def test_ends_active_conversation(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """end() sets status to completed."""
        mock_repository.get = AsyncMock(return_value=conversation)

        use_case = ChangeConversationStatus(repository=mock_repository)
        result = await use_case.end(conversation.id)

        assert result.status == "completed"
        assert conversation.is_completed
        mock_repository.save.assert_called_once_with(conversation)

    async def test_raises_when_not_found(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """end() raises ConversationNotFoundError for missing conversation."""
        fake_id = uuid4()
        mock_repository.get = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(ConversationNotFoundError):
            await use_case.end(fake_id)


class TestDelete:
    """Tests for ChangeConversationStatus.delete()."""

    async def test_deletes_conversation(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """delete() calls repository.delete and returns True."""
        mock_repository.delete = AsyncMock()

        use_case = ChangeConversationStatus(repository=mock_repository)
        result = await use_case.delete(conversation.id)

        assert result is True
        mock_repository.delete.assert_called_once_with(conversation.id)

    async def test_delete_propagates_not_found(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """delete() propagates ConversationNotFoundError from repository."""
        fake_id = uuid4()
        mock_repository.delete = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = ChangeConversationStatus(repository=mock_repository)

        with pytest.raises(ConversationNotFoundError):
            await use_case.delete(fake_id)
