"""
Unit tests for Message entity.

Tests for Message factory methods and entity behavior.
"""

from datetime import UTC, datetime
from uuid import UUID,uuid4

import pytest

from src.core.entities.message import Message, MessageRole
from src.core.exceptions import InvalidMessageContentError


class TestMessageCreate:
    """Tests for Message.create() factory method."""

    def test_create_user_message_with_valid_content(self):
        """Should create message with generated UUID and timestamp."""
        content = "Hello, I need help with English"
        msg = Message.create(content=content, role=MessageRole.USER)

        assert isinstance(msg.id, UUID)
        assert msg.content == content
        assert msg.role == MessageRole.USER
        assert isinstance(msg.created_at, datetime)
        assert msg.created_at.tzinfo == UTC
        assert msg.feedback is None

    def test_create_coach_message(self):
        """Should create coach message with correct role."""
        msg = Message.create(content="Let's practice!", role=MessageRole.COACH)
        assert msg.role == MessageRole.COACH

    @pytest.mark.parametrize(
        "invalid_content",
        [
            "",
            "   ",
            "\n\t  ",
            "   \n\n\t\t   ",
            None,
        ],
    )
    def test_create_with_invalid_content_raises_error(self, invalid_content):
        """Should reject empty, whitespace-only, or None content."""
        with pytest.raises(InvalidMessageContentError, match="cannot be empty"):
            Message.create(content=invalid_content, role=MessageRole.USER)


class TestMessageReconstitute:
    """Tests for Message.reconstitute() loader method."""

    def test_reconstitute_without_feedback(self):
        """Should reconstruct message from persistence data without validation."""
        msg_id = uuid4()
        created = datetime(2025, 1, 15, 10, 30, tzinfo=UTC)

        msg = Message.reconstitute(
            id=msg_id,
            content="Stored message",
            role=MessageRole.USER,
            created_at=created,
        )

        assert msg.id == msg_id
        assert msg.content == "Stored message"
        assert msg.role == MessageRole.USER
        assert msg.created_at == created
        assert msg.feedback is None

    def test_reconstitute_with_feedback(self, sample_feedback):
        """Should reconstruct message with attached feedback."""
        msg = Message.reconstitute(
            id=uuid4(),
            content="Message with feedback",
            role=MessageRole.USER,
            created_at=datetime.now(UTC),
            feedback=sample_feedback,
        )

        assert msg.feedback == sample_feedback

    def test_reconstitute_skips_validation(self):
        """Should allow invalid data when reconstituting (trusts persistence)."""
        msg = Message.reconstitute(
            id=uuid4(),
            content="",  # Invalid but allowed in reconstitute
            role=MessageRole.USER,
            created_at=datetime.now(UTC),
        )
        assert msg.content == ""


class TestMessageAttachFeedback:
    """Tests for Message.attach_feedback() method."""

    def test_attach_feedback_to_user_message(self, sample_feedback):
        """Should attach feedback to user message."""
        msg = Message.create(content="Hello", role=MessageRole.USER)

        msg.attach_feedback(sample_feedback)

        assert msg.feedback == sample_feedback

    def test_attach_feedback_to_coach_message_raises(self, sample_feedback):
        """Should reject attaching feedback to coach messages."""
        msg = Message.create(content="Hi there!", role=MessageRole.COACH)

        with pytest.raises(InvalidMessageContentError, match="Only user messages"):
            msg.attach_feedback(sample_feedback)

    def test_attach_feedback_when_already_has_feedback_raises(self, sample_feedback):
        """Should reject duplicate feedback attachment."""
        msg = Message.create(content="Hello", role=MessageRole.USER)
        msg.attach_feedback(sample_feedback)

        from src.core.entities.feedback import Feedback

        other_feedback = Feedback.create(corrections=[], suggestions=["Other"])

        with pytest.raises(InvalidMessageContentError, match="already has feedback"):
            msg.attach_feedback(other_feedback)


