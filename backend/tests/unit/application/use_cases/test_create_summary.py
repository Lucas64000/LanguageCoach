"""
Unit tests for CreateSummary use case.

Tests summary creation when a conversation is completed.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.use_case_dtos import (
    ConversationSummaryOutput,
    CreateSummaryInput,
)
from src.application.use_cases.create_summary import CreateSummary
from src.core.entities.conversation import Conversation
from src.core.entities.conversation_summary import ConversationSummary
from src.core.entities.message import MessageRole
from src.core.exceptions import ConversationNotFoundError, InvalidConversationStateError


class TestCreateSummary:
    """Tests for CreateSummary use case."""

    @pytest.fixture
    def conversation_with_messages(self) -> Conversation:
        """Create a completed conversation with messages for testing."""
        conv = Conversation.create(context_topic="Coffee shop practice")
        conv.add_message("Hello, I would like a coffee please", MessageRole.USER)
        conv.add_message("Of course! What size would you like?", MessageRole.COACH)
        conv.add_message("A large one, thanks", MessageRole.USER)
        conv.add_message("Coming right up!", MessageRole.COACH)
        conv.end()  # Mark as completed
        return conv

    @pytest.fixture
    def sample_summary(self) -> ConversationSummary:
        """Create sample summary for provider mock."""
        return ConversationSummary.create(
            fluency_score=80,
            strengths=["Good politeness", "Clear requests"],
            weaknesses=["Could use more varied vocabulary"],
            overall_remarks="Great coffee shop interaction!",
        )

    async def test_creates_summary_for_completed_conversation(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
        conversation_with_messages: Conversation,
        sample_summary: ConversationSummary,
    ) -> None:
        """execute() returns summary for completed conversation."""
        mock_repository.get = AsyncMock(return_value=conversation_with_messages)
        mock_summary_provider.create_summary = AsyncMock(return_value=sample_summary)

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )
        result = await use_case.execute(
            CreateSummaryInput(conversation_id=conversation_with_messages.id)
        )

        assert isinstance(result, ConversationSummaryOutput)
        assert result.fluency_score == 80
        assert "Good politeness" in result.strengths
        assert "Could use more varied vocabulary" in result.weaknesses
        mock_summary_provider.create_summary.assert_called_once_with(
            conversation_with_messages
        )

    async def test_calls_provider_with_conversation(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
        conversation_with_messages: Conversation,
        sample_summary: ConversationSummary,
    ) -> None:
        """execute() passes conversation to provider."""
        mock_repository.get = AsyncMock(return_value=conversation_with_messages)
        mock_summary_provider.create_summary = AsyncMock(return_value=sample_summary)

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )
        await use_case.execute(
            CreateSummaryInput(conversation_id=conversation_with_messages.id)
        )

        mock_summary_provider.create_summary.assert_called_once()
        call_args = mock_summary_provider.create_summary.call_args[0]
        assert call_args[0].id == conversation_with_messages.id

    async def test_raises_when_conversation_not_found(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
    ) -> None:
        """execute() raises ConversationNotFoundError for missing conversation."""
        fake_id = uuid4()
        mock_repository.get = AsyncMock(
            side_effect=ConversationNotFoundError(f"Conversation {fake_id} not found")
        )

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )

        with pytest.raises(ConversationNotFoundError):
            await use_case.execute(CreateSummaryInput(conversation_id=fake_id))

    async def test_raises_when_conversation_not_completed(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
    ) -> None:
        """execute() raises InvalidConversationStateError for active conversation."""
        active_conv = Conversation.create(context_topic="Active conversation")
        active_conv.add_message("Hello", MessageRole.USER)
        # Not calling .end() - conversation is still active

        mock_repository.get = AsyncMock(return_value=active_conv)

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )

        with pytest.raises(InvalidConversationStateError, match="must be completed"):
            await use_case.execute(CreateSummaryInput(conversation_id=active_conv.id))

    async def test_raises_when_conversation_archived(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
    ) -> None:
        """execute() raises InvalidConversationStateError for archived conversation."""
        archived_conv = Conversation.create(context_topic="Archived conversation")
        archived_conv.add_message("Hello", MessageRole.USER)
        archived_conv.archive()

        mock_repository.get = AsyncMock(return_value=archived_conv)

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )

        with pytest.raises(InvalidConversationStateError, match="must be completed"):
            await use_case.execute(CreateSummaryInput(conversation_id=archived_conv.id))

    async def test_raises_when_no_messages(
        self,
        mock_repository: AsyncMock,
        mock_summary_provider: AsyncMock,
    ) -> None:
        """execute() raises InvalidConversationStateError for empty conversation."""
        empty_conv = Conversation.create(context_topic="Empty conversation")
        empty_conv.end()  # Completed but no messages

        mock_repository.get = AsyncMock(return_value=empty_conv)

        use_case = CreateSummary(
            repository=mock_repository,
            summary_provider=mock_summary_provider,
        )

        with pytest.raises(InvalidConversationStateError, match="no messages"):
            await use_case.execute(CreateSummaryInput(conversation_id=empty_conv.id))
