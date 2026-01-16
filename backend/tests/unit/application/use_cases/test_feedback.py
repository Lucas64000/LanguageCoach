"""
Unit tests for FeedbackUseCases.

Tests both requesting and rating feedback functionality.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.use_case_dtos import RateFeedbackInput, RequestFeedbackInput
from src.application.mappers import FeedbackMapper
from src.application.use_cases.feedback import FeedbackUseCases
from src.core.entities.conversation import Conversation
from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole
from src.core.exceptions import (
    FeedbackNotFoundError,
    InvalidMessageContentError,
    MessageNotFoundError,
)


class TestRequestFeedback:
    """Tests for FeedbackUseCases.request()."""

    async def test_rejects_coach_message(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_feedback: Feedback,
    ) -> None:
        """request() raises for COACH messages."""
        conv = Conversation.create(context_topic="coffee_shop")
        coach_msg = conv.add_message("Hello! How can I help?", MessageRole.COACH)
        mock_repository.get_by_message_id.return_value = conv
        mock_feedback_provider.analyze_message.return_value = sample_feedback

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)

        with pytest.raises(InvalidMessageContentError, match="Only user messages"):
            await use_case.request(RequestFeedbackInput(message_id=coach_msg.id))

    async def test_returns_feedback(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_feedback: Feedback,
        sample_conversation_with_message: tuple[Conversation, Message],
    ) -> None:
        """request() returns feedback from provider."""
        conv, msg = sample_conversation_with_message
        mock_repository.get_by_message_id.return_value = conv
        mock_feedback_provider.analyze_message.return_value = sample_feedback

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)
        result = await use_case.request(RequestFeedbackInput(message_id=msg.id))

        assert result == FeedbackMapper.to_output(sample_feedback)
        mock_repository.get_by_message_id.assert_called_once_with(msg.id)
        mock_feedback_provider.analyze_message.assert_called_once_with(msg)

    async def test_attaches_feedback_to_message(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_feedback: Feedback,
        sample_conversation_with_message: tuple[Conversation, Message],
    ) -> None:
        """request() attaches feedback to the message."""
        conv, msg = sample_conversation_with_message
        mock_repository.get_by_message_id.return_value = conv
        mock_feedback_provider.analyze_message.return_value = sample_feedback

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)
        await use_case.request(RequestFeedbackInput(message_id=msg.id))

        # Verify feedback was attached to the message
        assert msg.feedback == sample_feedback

    async def test_saves_conversation(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_feedback: Feedback,
        sample_conversation_with_message: tuple[Conversation, Message],
    ) -> None:
        """request() persists the updated conversation."""
        conv, msg = sample_conversation_with_message
        mock_repository.get_by_message_id.return_value = conv
        mock_feedback_provider.analyze_message.return_value = sample_feedback

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)
        await use_case.request(RequestFeedbackInput(message_id=msg.id))

        mock_repository.save.assert_called_once_with(conv)

    async def test_raises_when_message_not_found(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
    ) -> None:
        """request() raises MessageNotFoundError when message not in repo."""
        mock_repository.get_by_message_id.side_effect = MessageNotFoundError(
            "Message not found"
        )

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)

        with pytest.raises(MessageNotFoundError):
            await use_case.request(RequestFeedbackInput(message_id=uuid4()))

    async def test_raises_when_message_already_has_feedback(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_feedback: Feedback,
        sample_conversation_with_message: tuple[Conversation, Message],
    ) -> None:
        """request() raises when message already has feedback."""
        conv, msg = sample_conversation_with_message
        # Attach initial feedback
        msg.attach_feedback(sample_feedback)

        mock_repository.get_by_message_id.return_value = conv
        # Provider returns new feedback
        new_feedback = Feedback.create(corrections=[], suggestions=["New suggestion"])
        mock_feedback_provider.analyze_message.return_value = new_feedback

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)

        with pytest.raises(InvalidMessageContentError, match="already has feedback"):
            await use_case.request(RequestFeedbackInput(message_id=msg.id))


class TestRateFeedback:
    """Tests for FeedbackUseCases.rate()."""

    async def test_updates_existing_rating(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
        sample_conversation_with_feedback: tuple[Conversation, Message],
    ) -> None:
        """rate() updates rating if called multiple times."""
        conv, msg = sample_conversation_with_feedback
        mock_repository.get_by_message_id.return_value = conv

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)

        # 1. Initial negative rating with comment
        input1 = RateFeedbackInput(
            message_id=msg.id,
            rating=False,
            comment="Not helpful",
        )
        result1 = await use_case.rate(input1)

        assert result1.user_rating is False
        assert result1.user_comment == "Not helpful"
        assert msg.feedback.user_rating is False
        assert msg.feedback.user_comment == "Not helpful"
        mock_repository.save.assert_called_with(conv)

        # 2. Update to positive rating (should verify comment is cleared by entity logic)
        input2 = RateFeedbackInput(
            message_id=msg.id,
            rating=True,
            comment=None,
        )
        result2 = await use_case.rate(input2)

        assert result2.user_rating is True
        assert result2.user_comment is None
        assert msg.feedback.user_rating is True
        assert msg.feedback.user_comment is None

        # Verify save called again
        assert mock_repository.save.call_count == 2

    async def test_raises_if_feedback_not_found(
        self,
        mock_repository: AsyncMock,
        mock_feedback_provider: AsyncMock,
    ) -> None:
        """rate() raises FeedbackNotFoundError if message has no feedback."""
        conv = Conversation.create(context_topic="test")
        msg = conv.add_message("test", MessageRole.USER)
        # No feedback attached

        mock_repository.get_by_message_id.return_value = conv

        use_case = FeedbackUseCases(mock_repository, mock_feedback_provider)
        input_dto = RateFeedbackInput(message_id=msg.id, rating=True)

        with pytest.raises(FeedbackNotFoundError):
            await use_case.rate(input_dto)
