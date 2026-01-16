"""
Tests for ConversationSummary entity.

Tests factory method, validation, and reconstitution.
"""

import pytest
from uuid import uuid4
from datetime import datetime, UTC

from src.core.entities.conversation_summary import ConversationSummary
from src.core.exceptions import InvalidFeedbackError


class TestConversationSummaryCreate:
    """Tests for ConversationSummary.create() factory method."""

    def test_create_valid_summary(self) -> None:
        """create() returns valid summary with all fields."""
        summary = ConversationSummary.create(
            fluency_score=75,
            strengths=["Good vocabulary", "Natural phrasing"],
            weaknesses=["Verb tenses", "Article usage"],
            overall_remarks="Good progress overall.",
        )

        assert summary.id is not None
        assert summary.fluency_score == 75
        assert summary.strengths == ["Good vocabulary", "Natural phrasing"]
        assert summary.weaknesses == ["Verb tenses", "Article usage"]
        assert summary.overall_remarks == "Good progress overall."
        assert summary.created_at is not None

    @pytest.mark.parametrize("score", [0, 100])
    def test_create_accepts_boundary_scores(self, score: int) -> None:
        """create() accepts boundary fluency scores."""
        summary = ConversationSummary.create(
            fluency_score=score,
            strengths=[],
            weaknesses=[],
            overall_remarks="OK",
        )

        assert summary.fluency_score == score


    def test_create_rejects_score_below_zero(self) -> None:
        """create() raises InvalidFeedbackError for score < 0."""
        with pytest.raises(InvalidFeedbackError, match="between 0 and 100"):
            ConversationSummary.create(
                fluency_score=-1,
                strengths=[],
                weaknesses=[],
                overall_remarks="",
            )

    def test_create_rejects_score_above_hundred(self) -> None:
        """create() raises InvalidFeedbackError for score > 100."""
        with pytest.raises(InvalidFeedbackError, match="between 0 and 100"):
            ConversationSummary.create(
                fluency_score=101,
                strengths=[],
                weaknesses=[],
                overall_remarks="",
            )


class TestConversationSummaryReconstitute:
    """Tests for ConversationSummary.reconstitute() loader method."""

    def test_reconstitute_restores_all_fields(self) -> None:
        """reconstitute() restores summary without validation."""
        known_id = uuid4()
        known_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=UTC)

        summary = ConversationSummary.reconstitute(
            id=known_id,
            fluency_score=85,
            strengths=["Good grammar"],
            weaknesses=["Pronunciation"],
            overall_remarks="Well done!",
            created_at=known_time,
        )

        assert summary.id == known_id
        assert summary.fluency_score == 85
        assert summary.strengths == ["Good grammar"]
        assert summary.weaknesses == ["Pronunciation"]
        assert summary.overall_remarks == "Well done!"
        assert summary.created_at == known_time

    def test_reconstitute_skips_validation(self) -> None:
        """reconstitute() allows invalid scores (trusted persistence data)."""
        # This simulates corrupted data - reconstitute trusts the DB
        summary = ConversationSummary.reconstitute(
            id=uuid4(),
            fluency_score=150,  # Invalid but accepted
            strengths=[],
            weaknesses=[],
            overall_remarks="",
            created_at=datetime.now(UTC),
        )

        assert summary.fluency_score == 150
