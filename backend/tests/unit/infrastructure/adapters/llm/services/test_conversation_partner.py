"""Tests for LLMConversationPartner service."""

import pytest

from src.core.entities.message import Message, MessageRole
from src.core.value_objects import ConversationTone
from src.infrastructure.adapters.llm.clients.base import LLMResponse
from src.infrastructure.adapters.llm.services.conversation_partner import (
    LLMConversationPartner,
)


@pytest.fixture
def sample_messages():
    """Sample conversation messages."""
    return [
        Message.create(role=MessageRole.USER, content="Hello"),
        Message.create(role=MessageRole.COACH, content="Hi there!"),
    ]


class TestLLMConversationPartner:
    """Tests for LLMConversationPartner service."""

    @pytest.mark.asyncio
    async def test_generate_response(self, mock_client, sample_messages):
        """generate_response calls client and returns content."""
        mock_client.complete.return_value = LLMResponse(content="Hello there!")

        partner = LLMConversationPartner(mock_client)
        response = await partner.generate_response("coffee shop", sample_messages)

        assert response == "Hello there!"
        mock_client.complete.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tone", "expected_text"),
        [
            (ConversationTone.FORMAL, "formal and precise"),
            (ConversationTone.FRIENDLY, "friendly and warm"),
            (ConversationTone.ENCOURAGING, "enthusiastic and motivating"),
            (ConversationTone.PATIENT, "patient and gentle"),
        ],
    )
    async def test_generate_response_with_tone(
        self, mock_client, sample_messages, tone, expected_text
    ):
        """generate_response uses tone in system prompt."""
        mock_client.complete.return_value = LLMResponse(content="Response")

        partner = LLMConversationPartner(mock_client)
        await partner.generate_response("coffee shop", sample_messages, tone=tone)

        call_args = mock_client.complete.call_args
        messages = call_args[0][0]
        system_message = messages[0]
        assert system_message.role == "system"
        assert expected_text in system_message.content.lower()

    @pytest.mark.asyncio
    async def test_generate_response_stream(self, mock_client, sample_messages):
        """generate_response_stream yields tokens."""

        async def mock_stream(*args, **kwargs):
            yield "Hello"
            yield " world"

        mock_client.complete_stream = mock_stream

        partner = LLMConversationPartner(mock_client)
        chunks = []
        async for chunk in partner.generate_response_stream("context", sample_messages):
            chunks.append(chunk)

        assert chunks == ["Hello", " world"]
