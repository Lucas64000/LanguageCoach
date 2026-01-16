"""
Unit tests for FeedbackMapper.

Tests Entity → Application DTO mapping.
"""

import pytest

from src.application.dtos.use_case_dtos import CorrectionOutput, FeedbackOutput
from src.application.mappers.feedback_mapper import FeedbackMapper
from src.core.entities.feedback import Feedback
from src.core.value_objects import Correction, CorrectionType


class TestFeedbackMapperToOutput:
    """Tests for FeedbackMapper.to_output()."""

    def test_maps_corrections_to_correction_output(
        self, sample_feedback: Feedback
    ) -> None:
        """to_output() converts Correction VOs to CorrectionOutput DTOs."""
        result = FeedbackMapper.to_output(sample_feedback)

        assert len(result.corrections) == 1
        correction = result.corrections[0]
        assert isinstance(correction, CorrectionOutput)
        assert correction.original == "I go yesterday"
        assert correction.corrected == "I went yesterday"
        assert correction.explanation == "Use past tense for past actions"
        assert correction.correction_type == "grammar"

    def test_maps_suggestions_to_tuple(self, sample_feedback: Feedback) -> None:
        """to_output() converts suggestions list to tuple."""
        result = FeedbackMapper.to_output(sample_feedback)

        assert isinstance(result.suggestions, tuple)
        assert len(result.suggestions) == 2
        assert "Try using more descriptive verbs" in result.suggestions

    def test_preserves_id_and_timestamps(self, sample_feedback: Feedback) -> None:
        """to_output() preserves feedback ID and created_at."""
        result = FeedbackMapper.to_output(sample_feedback)

        assert result.id == sample_feedback.id
        assert result.created_at == sample_feedback.created_at

    def test_maps_user_rating_when_present(
        self, sample_feedback_with_rating: Feedback
    ) -> None:
        """to_output() includes user_rating and user_comment when set."""
        result = FeedbackMapper.to_output(sample_feedback_with_rating)

        assert result.user_rating is False
        assert result.user_comment == "Could be clearer"

    def test_maps_user_rating_as_none_when_absent(
        self, sample_feedback: Feedback
    ) -> None:
        """to_output() returns None for user_rating when not rated."""
        result = FeedbackMapper.to_output(sample_feedback)

        assert result.user_rating is None
        assert result.user_comment is None

    def test_returns_feedback_output_type(self, sample_feedback: Feedback) -> None:
        """to_output() returns FeedbackOutput dataclass."""
        result = FeedbackMapper.to_output(sample_feedback)

        assert isinstance(result, FeedbackOutput)

    def test_handles_empty_corrections(self) -> None:
        """to_output() handles feedback with no corrections."""
        feedback = Feedback.create(
            corrections=[],
            suggestions=["Great job!"],
        )

        result = FeedbackMapper.to_output(feedback)

        assert result.corrections == ()
        assert len(result.suggestions) == 1

    def test_handles_multiple_correction_types(self) -> None:
        """to_output() correctly maps different correction types."""
        corrections = [
            Correction(
                original="I go",
                corrected="I went",
                explanation="Past tense",
                correction_type=CorrectionType.GRAMMAR,
            ),
            Correction(
                original="big",
                corrected="enormous",
                explanation="More descriptive",
                correction_type=CorrectionType.VOCABULARY,
            ),
            Correction(
                original="I want for to go",
                corrected="I want to go",
                explanation="Remove extra word",
                correction_type=CorrectionType.PHRASING,
            ),
        ]
        feedback = Feedback.create(corrections=corrections, suggestions=[])

        result = FeedbackMapper.to_output(feedback)

        assert len(result.corrections) == 3
        assert result.corrections[0].correction_type == "grammar"
        assert result.corrections[1].correction_type == "vocabulary"
        assert result.corrections[2].correction_type == "phrasing"
