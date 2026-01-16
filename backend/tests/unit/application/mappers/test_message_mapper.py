"""
Unit tests for MessageMapper.

Tests Entity → Application DTO mapping for messages.
"""

import pytest

from src.application.dtos.use_case_dtos import FeedbackOutput, MessageOutput
from src.application.mappers.message_mapper import MessageMapper
from src.core.entities.conversation import Conversation
from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole


class TestMessageMapperToOutput:
    """Tests for MessageMapper.to_output()."""

    def test_maps_basic_fields(self, sample_conversation: Conversation) -> None:
        """to_output() maps id, content, role, created_at."""
        message = sample_conversation.messages[0]

        result = MessageMapper.to_output(message)

        assert result.id == message.id
        assert result.content == "Hello, I want coffee please"
        assert result.role == "user"
        assert result.created_at == message.created_at

    def test_maps_role_value_to_string(self, sample_conversation: Conversation) -> None:
        """to_output() converts MessageRole enum to string value."""
        user_msg = sample_conversation.messages[0]
        coach_msg = sample_conversation.messages[1]

        user_result = MessageMapper.to_output(user_msg)
        coach_result = MessageMapper.to_output(coach_msg)

        assert user_result.role == "user"
        assert coach_result.role == "coach"

    def test_includes_feedback_when_present(
        self, sample_message_with_feedback: tuple[Conversation, Message]
    ) -> None:
        """to_output() includes mapped feedback when attached."""
        _, message = sample_message_with_feedback

        result = MessageMapper.to_output(message)

        assert result.feedback is not None
        assert isinstance(result.feedback, FeedbackOutput)
        assert len(result.feedback.corrections) == 1

    def test_feedback_is_none_when_absent(
        self, sample_conversation: Conversation
    ) -> None:
        """to_output() returns None for feedback when not attached."""
        message = sample_conversation.messages[0]

        result = MessageMapper.to_output(message)

        assert result.feedback is None

    def test_returns_message_output_type(
        self, sample_conversation: Conversation
    ) -> None:
        """to_output() returns MessageOutput dataclass."""
        message = sample_conversation.messages[0]

        result = MessageMapper.to_output(message)

        assert isinstance(result, MessageOutput)
