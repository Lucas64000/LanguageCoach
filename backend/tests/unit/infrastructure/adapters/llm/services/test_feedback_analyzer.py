"""Tests for LLMFeedbackAnalyzer service."""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole
from src.core.exceptions import FeedbackAnalysisError
from src.core.value_objects import CorrectionType
from src.infrastructure.adapters.llm.clients.base import LLMResponse
from src.infrastructure.adapters.llm.services.feedback_analyzer import (
    LLMFeedbackAnalyzer,
)


@pytest.fixture
def sample_message():
    """Single sample message for feedback analysis."""
    return Message.reconstitute(
        id=uuid4(),
        content="She go to school yesterday",
        role=MessageRole.USER,
        created_at=datetime.now(UTC),
    )


class TestLLMFeedbackAnalyzer:
    """Tests for LLMFeedbackAnalyzer service."""

    @pytest.mark.asyncio
    async def test_analyze_message_success(self, mock_client, sample_message):
        """Successful analysis returns Feedback with corrections."""
        mock_client.complete.return_value = LLMResponse(
            content='''{
                "corrections": [
                    {"original": "go", "corrected": "went", "explanation": "Past tense", "type": "grammar"}
                ],
                "suggestions": ["Practice past tense"]
            }'''
        )

        analyzer = LLMFeedbackAnalyzer(mock_client)
        feedback = await analyzer.analyze_message(sample_message)

        assert isinstance(feedback, Feedback)
        assert len(feedback.corrections) == 1
        assert feedback.corrections[0].original == "go"
        assert feedback.corrections[0].corrected == "went"
        assert feedback.corrections[0].correction_type == CorrectionType.GRAMMAR
        assert feedback.suggestions == ["Practice past tense"]

    @pytest.mark.asyncio
    async def test_analyze_message_empty_feedback(self, mock_client, sample_message):
        """No errors returns empty feedback."""
        mock_client.complete.return_value = LLMResponse(
            content='{"corrections": [], "suggestions": []}'
        )

        analyzer = LLMFeedbackAnalyzer(mock_client)
        feedback = await analyzer.analyze_message(sample_message)

        assert feedback.corrections == []
        assert feedback.suggestions == []

    @pytest.mark.asyncio
    async def test_analyze_message_invalid_json(self, mock_client, sample_message):
        """Invalid JSON raises FeedbackAnalysisError."""
        mock_client.complete.return_value = LLMResponse(content="{invalid json")

        analyzer = LLMFeedbackAnalyzer(mock_client)

        with pytest.raises(FeedbackAnalysisError, match="Invalid JSON"):
            await analyzer.analyze_message(sample_message)

    @pytest.mark.asyncio
    async def test_analyze_message_api_error(self, mock_client, sample_message):
        """API error raises FeedbackAnalysisError."""
        mock_client.complete.side_effect = Exception("API failure")

        analyzer = LLMFeedbackAnalyzer(mock_client)

        with pytest.raises(FeedbackAnalysisError, match="Feedback analysis failed"):
            await analyzer.analyze_message(sample_message)

    @pytest.mark.asyncio
    async def test_analyze_message_ignores_invalid_corrections(
        self, mock_client, sample_message
    ):
        """Invalid corrections are filtered out."""
        mock_client.complete.return_value = LLMResponse(
            content='''{
                "corrections": [
                    {"original": "", "corrected": "went", "type": "grammar"},
                    {"original": "go", "corrected": "", "type": "grammar"},
                    {"original": "go", "corrected": "went", "type": "INVALID"},
                    {"original": "good", "corrected": "well", "type": "vocabulary"}
                ],
                "suggestions": []
            }'''
        )

        analyzer = LLMFeedbackAnalyzer(mock_client)
        feedback = await analyzer.analyze_message(sample_message)

        # Only the last valid correction should remain
        assert len(feedback.corrections) == 1
        assert feedback.corrections[0].correction_type == CorrectionType.VOCABULARY
