"""Unit tests for Conversation entity.

Unit tests cover:
- Creation via factory methods with validation.
- Domain object reconstitution from persistence.
- Message history management and roles.
- State transition integrity and status updates.
- Tone and context validation rules.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4
import time
import pytest

from src.core.entities.conversation import Conversation, ConversationStatus
from src.core.entities.message import Message, MessageRole
from src.core.exceptions import (
    InvalidContextError,
    InvalidConversationStateError,
    InvalidMessageContentError,
)
from src.core.value_objects import ConversationTone


class TestConversationCreate:
    """Tests for Conversation.create() factory method."""

    def test_create_with_valid_context(self):
        """Should create conversation with generated UUID and timestamps."""
        conv = Conversation.create(context_topic="Job interview practice")

        assert isinstance(conv.id, UUID)
        assert conv.context_topic == "Job interview practice"
        assert conv.messages == []
        assert isinstance(conv.created_at, datetime)
        assert isinstance(conv.updated_at, datetime)
        assert conv.created_at.tzinfo == UTC
        assert conv.status == ConversationStatus.ACTIVE
        assert conv.tone == ConversationTone.FRIENDLY

    def test_create_with_custom_tone(self):
        """Should create conversation with specified tone."""
        conv = Conversation.create(
            context_topic="Business meeting",
            tone=ConversationTone.FORMAL,
        )
        assert conv.tone == ConversationTone.FORMAL

    def test_create_strips_whitespace_from_context(self):
        """Should trim leading/trailing whitespace from context."""
        conv = Conversation.create(context_topic="  Travel conversation  \n")
        assert conv.context_topic == "Travel conversation"

    @pytest.mark.parametrize(
        "invalid_context",
        [
            "",
            "   ",
            "\n\t  ",
            "   \n\n\t\t   ",
            None,
        ],
    )
    def test_create_with_invalid_context_raises_error(self, invalid_context):
        """Should reject empty, whitespace-only, or None context."""
        with pytest.raises(InvalidContextError, match="cannot be empty"):
            Conversation.create(context_topic=invalid_context)


class TestConversationReconstitute:
    """Tests for Conversation.reconstitute() loader method."""

    def test_reconstitute_with_all_fields(self):
        """Should reconstruct conversation from persistence."""
        conv_id = uuid4()
        created = datetime(2025, 1, 10, 8, 0, tzinfo=UTC)
        updated = datetime(2025, 1, 15, 12, 0, tzinfo=UTC)
        messages = [
            Message.create(content="Hello", role=MessageRole.USER),
        ]

        conv = Conversation.reconstitute(
            id=conv_id,
            context_topic="Email writing",
            messages=messages,
            created_at=created,
            updated_at=updated,
            status=ConversationStatus.COMPLETED,
            tone=ConversationTone.PATIENT,
        )

        assert conv.id == conv_id
        assert conv.context_topic == "Email writing"
        assert conv.messages == messages
        assert conv.created_at == created
        assert conv.updated_at == updated
        assert conv.status == ConversationStatus.COMPLETED
        assert conv.tone == ConversationTone.PATIENT

    def test_reconstitute_skips_validation(self):
        """Should allow invalid data when reconstituting."""
        conv = Conversation.reconstitute(
            id=uuid4(),
            context_topic="",  # Invalid but allowed
            messages=[],
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        assert conv.context_topic == ""


class TestConversationStatusProperties:
    """Tests for conversation status property helpers."""

    def test_is_active_property(self, active_conversation):
        """Should return True only when status is ACTIVE."""
        assert active_conversation.is_active is True

        active_conversation.status = ConversationStatus.COMPLETED
        assert active_conversation.is_active is False

    def test_is_archived_property(self, active_conversation):
        """Should return True only when status is ARCHIVED."""
        assert active_conversation.is_archived is False

        active_conversation.status = ConversationStatus.ARCHIVED
        assert active_conversation.is_archived is True

    def test_is_completed_property(self, active_conversation):
        """Should return True only when status is COMPLETED."""
        assert active_conversation.is_completed is False

        active_conversation.status = ConversationStatus.COMPLETED
        assert active_conversation.is_completed is True


class TestConversationArchive:
    """Tests for Conversation.archive() method."""

    def test_archive_active_conversation(self, active_conversation):
        """Should archive active conversation and update timestamp."""
        original_updated = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.archive()

        assert active_conversation.status == ConversationStatus.ARCHIVED
        assert active_conversation.updated_at > original_updated

    def test_archive_already_archived_raises_error(self, active_conversation):
        """Should prevent archiving an already archived conversation."""
        active_conversation.archive()

        with pytest.raises(
            InvalidConversationStateError, match="already archived"
        ):
            active_conversation.archive()

    def test_archive_completed_conversation_raises_error(self, active_conversation):
        """Should prevent archiving a completed conversation."""
        active_conversation.end()

        with pytest.raises(
            InvalidConversationStateError, match="Cannot archive a completed"
        ):
            active_conversation.archive()


class TestConversationRestore:
    """Tests for Conversation.restore() method."""

    def test_restore_archived_conversation(self, active_conversation):
        """Should restore archived conversation to active status."""
        active_conversation.archive()

        active_conversation.restore()

        assert active_conversation.status == ConversationStatus.ACTIVE
        assert active_conversation.is_active is True

    def test_restore_completed_conversation(self, active_conversation):
        """Should restore completed conversation to active status."""
        active_conversation.end()

        active_conversation.restore()

        assert active_conversation.status == ConversationStatus.ACTIVE

    def test_restore_already_active_raises_error(self, active_conversation):
        """Should prevent restoring an already active conversation."""
        with pytest.raises(
            InvalidConversationStateError, match="already active"
        ):
            active_conversation.restore()

    def test_restore_updates_timestamp(self, active_conversation):
        """Should update the updated_at timestamp when restoring."""
        active_conversation.archive()
        original_updated = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.restore()

        assert active_conversation.updated_at > original_updated


class TestConversationEnd:
    """Tests for Conversation.end() method."""

    def test_end_active_conversation(self, active_conversation):
        """Should mark active conversation as completed."""
        original_updated = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.end()

        assert active_conversation.status == ConversationStatus.COMPLETED
        assert active_conversation.updated_at > original_updated

    def test_end_already_completed_raises_error(self, active_conversation):
        """Should prevent ending an already completed conversation."""
        active_conversation.end()

        with pytest.raises(
            InvalidConversationStateError, match="already completed"
        ):
            active_conversation.end()

    def test_end_archived_conversation_raises_error(self, active_conversation):
        """Should prevent completing an archived conversation."""
        active_conversation.archive()

        with pytest.raises(
            InvalidConversationStateError, match="Cannot complete an archived"
        ):
            active_conversation.end()


class TestConversationAddMessage:
    """Tests for Conversation.add_message() method."""

    def test_add_message_creates_and_appends(self, active_conversation):
        """Should create message and add to conversation's message list."""
        msg = active_conversation.add_message(
            content="Hello coach", role=MessageRole.USER
        )

        assert isinstance(msg, Message)
        assert msg.content == "Hello coach"
        assert msg.role == MessageRole.USER
        assert len(active_conversation.messages) == 1
        assert active_conversation.messages[0] == msg

    def test_add_message_updates_timestamp(self, active_conversation):
        """Should update conversation's updated_at timestamp."""
        original_updated = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.add_message(content="Test", role=MessageRole.USER)

        assert active_conversation.updated_at > original_updated

    def test_add_multiple_messages_maintains_order(self, active_conversation):
        """Should maintain message order when adding multiple messages."""
        msg1 = active_conversation.add_message("First", MessageRole.USER)
        msg2 = active_conversation.add_message("Second", MessageRole.COACH)
        msg3 = active_conversation.add_message("Third", MessageRole.USER)

        assert len(active_conversation.messages) == 3
        assert active_conversation.messages == [msg1, msg2, msg3]

    def test_add_message_validates_content(self, active_conversation):
        """Should enforce message validation rules through factory."""
        with pytest.raises(InvalidMessageContentError):
            active_conversation.add_message(content="", role=MessageRole.USER)

    def test_add_message_to_conversation_with_existing_messages(
        self, conversation_with_messages
    ):
        """Should append to existing messages."""
        initial_count = len(conversation_with_messages.messages)

        new_msg = conversation_with_messages.add_message(
            "Another message", MessageRole.COACH
        )

        assert len(conversation_with_messages.messages) == initial_count + 1
        assert conversation_with_messages.messages[-1] == new_msg


class TestConversationTimestampManagement:
    """Tests for internal _touch() timestamp update across operations."""

    def test_touch_updates_timestamp_on_archive(self, active_conversation):
        """Archive should update timestamp via _touch()."""
        original = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.archive()

        assert active_conversation.updated_at > original

    def test_touch_updates_timestamp_on_restore(self, active_conversation):
        """Restore should update timestamp via _touch()."""
        active_conversation.archive()
        original = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.restore()

        assert active_conversation.updated_at > original

    def test_touch_updates_timestamp_on_end(self, active_conversation):
        """End should update timestamp via _touch()."""
        original = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.end()

        assert active_conversation.updated_at > original

    def test_touch_updates_timestamp_on_add_message(self, active_conversation):
        """Add message should update timestamp via _touch()."""
        original = active_conversation.updated_at
        time.sleep(0.001)

        active_conversation.add_message("Test", MessageRole.USER)

        assert active_conversation.updated_at > original
