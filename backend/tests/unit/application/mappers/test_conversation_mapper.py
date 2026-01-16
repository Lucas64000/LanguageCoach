"""
Unit tests for ConversationMapper.

Tests Entity → Application DTO mapping for conversations.
"""

import pytest

from src.application.dtos.use_case_dtos import (
    ConversationDetailOutput,
    ConversationOutput,
    ConversationStatusOutput,
)
from src.application.mappers.conversation_mapper import ConversationMapper
from src.core.entities.conversation import Conversation
from src.core.entities.message import MessageRole


class TestConversationMapperToOutput:
    """Tests for ConversationMapper.to_output()."""

    def test_maps_basic_fields(self, sample_conversation: Conversation) -> None:
        """to_output() maps id, context_topic, tone, status, timestamps."""
        result = ConversationMapper.to_output(sample_conversation)

        assert result.id == sample_conversation.id
        assert result.context_topic == "coffee shop"
        assert result.tone == "friendly"  # Default tone
        assert result.status == "active"
        assert result.created_at == sample_conversation.created_at
        assert result.updated_at == sample_conversation.updated_at

    def test_counts_messages(self, sample_conversation: Conversation) -> None:
        """to_output() correctly counts messages."""
        result = ConversationMapper.to_output(sample_conversation)

        assert result.message_count == 2

    def test_extracts_last_message(self, sample_conversation: Conversation) -> None:
        """to_output() extracts content of last message."""
        result = ConversationMapper.to_output(sample_conversation)

        assert result.last_message == "Of course! What type would you like?"

    def test_handles_no_messages(self) -> None:
        """to_output() returns None for last_message when no messages."""
        conv = Conversation.create(context_topic="empty")

        result = ConversationMapper.to_output(conv)

        assert result.message_count == 0
        assert result.last_message is None

    def test_returns_conversation_output_type(
        self, sample_conversation: Conversation
    ) -> None:
        """to_output() returns ConversationOutput dataclass."""
        result = ConversationMapper.to_output(sample_conversation)

        assert isinstance(result, ConversationOutput)


class TestConversationMapperToDetailOutput:
    """Tests for ConversationMapper.to_detail_output()."""

    def test_includes_all_messages(self, sample_conversation: Conversation) -> None:
        """to_detail_output() includes all messages as MessageOutput."""
        result = ConversationMapper.to_detail_output(sample_conversation)

        assert len(result.messages) == 2
        assert result.messages[0].content == "Hello, I want coffee please"
        assert result.messages[0].role == "user"
        assert result.messages[1].content == "Of course! What type would you like?"
        assert result.messages[1].role == "coach"

    def test_maps_basic_fields(self, sample_conversation: Conversation) -> None:
        """to_detail_output() maps conversation fields correctly."""
        result = ConversationMapper.to_detail_output(sample_conversation)

        assert result.id == sample_conversation.id
        assert result.context_topic == "coffee shop"
        assert result.tone == "friendly"
        assert result.status == "active"

    def test_returns_conversation_detail_output_type(
        self, sample_conversation: Conversation
    ) -> None:
        """to_detail_output() returns ConversationDetailOutput dataclass."""
        result = ConversationMapper.to_detail_output(sample_conversation)

        assert isinstance(result, ConversationDetailOutput)

    def test_messages_are_tuple(self, sample_conversation: Conversation) -> None:
        """to_detail_output() returns messages as tuple for immutability."""
        result = ConversationMapper.to_detail_output(sample_conversation)

        assert isinstance(result.messages, tuple)


class TestConversationMapperToStatusOutput:
    """Tests for ConversationMapper.to_status_output()."""

    def test_returns_id_and_status(self, sample_conversation: Conversation) -> None:
        """to_status_output() returns only id and status."""
        result = ConversationMapper.to_status_output(sample_conversation)

        assert result.id == sample_conversation.id
        assert result.status == "active"

    def test_reflects_archived_status(self) -> None:
        """to_status_output() reflects archived status."""
        conv = Conversation.create(context_topic="test")
        conv.archive()

        result = ConversationMapper.to_status_output(conv)

        assert result.status == "archived"

    def test_returns_conversation_status_output_type(
        self, sample_conversation: Conversation
    ) -> None:
        """to_status_output() returns ConversationStatusOutput dataclass."""
        result = ConversationMapper.to_status_output(sample_conversation)

        assert isinstance(result, ConversationStatusOutput)
