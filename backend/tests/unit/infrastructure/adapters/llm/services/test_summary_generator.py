"""Tests for LLMSummaryGenerator service."""

import pytest

from src.core.entities.conversation import Conversation
from src.core.entities.message import MessageRole
from src.core.exceptions import SummaryGenerationError
from src.infrastructure.adapters.llm.clients.base import LLMResponse
from src.infrastructure.adapters.llm.services.summary_generator import (
    LLMSummaryGenerator,
)


@pytest.fixture
def sample_conversation():
    """Sample completed conversation for summary generation."""
    conv = Conversation.create(context_topic="coffee shop")
    conv.add_message(content="I want coffee", role=MessageRole.USER)
    conv.add_message(content="What kind?", role=MessageRole.COACH)
    conv.add_message(content="A latte please", role=MessageRole.USER)
    conv.end()
    return conv


class TestLLMSummaryGenerator:
    """Tests for LLMSummaryGenerator service."""

    @pytest.mark.asyncio
    async def test_create_summary_success(self, mock_client, sample_conversation):
        """Successful summary generation."""
        mock_client.complete.return_value = LLMResponse(
            content='''{
                "fluency_score": 75,
                "strengths": ["Good vocabulary"],
                "weaknesses": ["Grammar needs work"],
                "overall_remarks": "Keep practicing!"
            }'''
        )

        generator = LLMSummaryGenerator(mock_client)
        summary = await generator.create_summary(sample_conversation)

        assert summary.fluency_score == 75
        assert summary.strengths == ["Good vocabulary"]
        assert summary.weaknesses == ["Grammar needs work"]
        assert summary.overall_remarks == "Keep practicing!"

    @pytest.mark.asyncio
    async def test_create_summary_clamps_score(self, mock_client, sample_conversation):
        """Score is clamped to 0-100 range."""
        mock_client.complete.return_value = LLMResponse(
            content='''{
                "fluency_score": 150,
                "strengths": [],
                "weaknesses": [],
                "overall_remarks": ""
            }'''
        )

        generator = LLMSummaryGenerator(mock_client)
        summary = await generator.create_summary(sample_conversation)

        assert summary.fluency_score == 100

    @pytest.mark.asyncio
    async def test_create_summary_invalid_json(self, mock_client, sample_conversation):
        """Invalid JSON raises SummaryGenerationError."""
        mock_client.complete.return_value = LLMResponse(content="{invalid")

        generator = LLMSummaryGenerator(mock_client)

        with pytest.raises(SummaryGenerationError, match="Invalid JSON"):
            await generator.create_summary(sample_conversation)

    @pytest.mark.asyncio
    async def test_create_summary_api_error(self, mock_client, sample_conversation):
        """API error raises SummaryGenerationError."""
        mock_client.complete.side_effect = Exception("API failure")

        generator = LLMSummaryGenerator(mock_client)

        with pytest.raises(SummaryGenerationError, match="Summary generation failed"):
            await generator.create_summary(sample_conversation)
