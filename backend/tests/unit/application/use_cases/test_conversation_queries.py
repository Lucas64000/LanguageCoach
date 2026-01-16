"""
Unit tests for ConversationQueries use case.

Tests read operations: get, list_all, list_by_status.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.use_cases.conversation_queries import ConversationQueries
from src.core.entities.conversation import Conversation
from src.core.exceptions import ConversationNotFoundError
from src.core.value_objects import ConversationStatus


class TestGet:
    """Tests for ConversationQueries.get()."""

    async def test_returns_conversation_detail(
        self,
        mock_repository: AsyncMock,
        sample_conversation: Conversation,
    ) -> None:
        """get() returns ConversationDetailOutput with messages."""
        mock_repository.get = AsyncMock(return_value=sample_conversation)

        use_case = ConversationQueries(repository=mock_repository)
        result = await use_case.get(sample_conversation.id)

        assert result.id == sample_conversation.id
        assert result.context_topic == "coffee shop"
        assert len(result.messages) == 2
        mock_repository.get.assert_called_once_with(sample_conversation.id)

    async def test_raises_when_not_found(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """get() raises ConversationNotFoundError for missing conversation."""
        fake_id = uuid4()
        mock_repository.get = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = ConversationQueries(repository=mock_repository)

        with pytest.raises(ConversationNotFoundError):
            await use_case.get(fake_id)


class TestListAll:
    """Tests for ConversationQueries.list_all()."""

    async def test_returns_all_conversations(
        self,
        mock_repository: AsyncMock,
        sample_conversation: Conversation,
        conversation: Conversation,
    ) -> None:
        """list_all() returns list of ConversationOutput."""
        mock_repository.list_all = AsyncMock(
            return_value=[sample_conversation, conversation]
        )

        use_case = ConversationQueries(repository=mock_repository)
        result = await use_case.list_all()

        assert len(result) == 2
        assert result[0].id == sample_conversation.id
        assert result[1].id == conversation.id
        mock_repository.list_all.assert_called_once()

    async def test_returns_empty_list(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """list_all() returns empty list when no conversations exist."""
        mock_repository.list_all = AsyncMock(return_value=[])

        use_case = ConversationQueries(repository=mock_repository)
        result = await use_case.list_all()

        assert result == []


class TestListByStatus:
    """Tests for ConversationQueries.list_by_status()."""

    async def test_returns_filtered_conversations(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """list_by_status() returns only conversations with matching status."""
        conversation.archive()
        mock_repository.list_by_status = AsyncMock(return_value=[conversation])

        use_case = ConversationQueries(repository=mock_repository)
        result = await use_case.list_by_status(ConversationStatus.ARCHIVED)

        assert len(result) == 1
        assert result[0].status == "archived"
        mock_repository.list_by_status.assert_called_once_with(
            ConversationStatus.ARCHIVED
        )

    async def test_returns_empty_for_no_matches(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """list_by_status() returns empty list when no conversations match."""
        mock_repository.list_by_status = AsyncMock(return_value=[])

        use_case = ConversationQueries(repository=mock_repository)
        result = await use_case.list_by_status(ConversationStatus.COMPLETED)

        assert result == []
