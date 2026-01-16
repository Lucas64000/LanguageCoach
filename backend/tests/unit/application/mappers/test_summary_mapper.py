"""
Unit tests for SummaryMapper.

Tests Entity → Application DTO mapping for conversation summaries.
"""

import pytest

from src.application.dtos.use_case_dtos import ConversationSummaryOutput
from src.application.mappers.summary_mapper import SummaryMapper
from src.core.entities.conversation_summary import ConversationSummary


class TestSummaryMapperToOutput:
    """Tests for SummaryMapper.to_output()."""

    def test_maps_basic_fields(self, sample_summary: ConversationSummary) -> None:
        """to_output() maps id, fluency_score, overall_remarks, created_at."""
        result = SummaryMapper.to_output(sample_summary)

        assert result.id == sample_summary.id
        assert result.fluency_score == 75
        assert result.overall_remarks == "Great progress! Keep practicing verb conjugations."
        assert result.created_at == sample_summary.created_at

    def test_converts_strengths_to_tuple(
        self, sample_summary: ConversationSummary
    ) -> None:
        """to_output() converts strengths list to tuple."""
        result = SummaryMapper.to_output(sample_summary)

        assert isinstance(result.strengths, tuple)
        assert len(result.strengths) == 2
        assert "Good vocabulary" in result.strengths
        assert "Natural flow" in result.strengths

    def test_converts_weaknesses_to_tuple(
        self, sample_summary: ConversationSummary
    ) -> None:
        """to_output() converts weaknesses list to tuple."""
        result = SummaryMapper.to_output(sample_summary)

        assert isinstance(result.weaknesses, tuple)
        assert len(result.weaknesses) == 2
        assert "Verb tenses" in result.weaknesses
        assert "Prepositions" in result.weaknesses

    def test_returns_conversation_summary_output_type(
        self, sample_summary: ConversationSummary
    ) -> None:
        """to_output() returns ConversationSummaryOutput dataclass."""
        result = SummaryMapper.to_output(sample_summary)

        assert isinstance(result, ConversationSummaryOutput)

    def test_handles_empty_strengths_and_weaknesses(self) -> None:
        """to_output() handles summary with empty lists."""
        summary = ConversationSummary.create(
            fluency_score=50,
            strengths=[],
            weaknesses=[],
            overall_remarks="Average performance.",
        )

        result = SummaryMapper.to_output(summary)

        assert result.strengths == ()
        assert result.weaknesses == ()
