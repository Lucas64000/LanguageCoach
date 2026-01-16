"""
Unit tests for Feedback entity and Correction value object.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.entities.feedback import Feedback
from src.core.value_objects import Correction, CorrectionType


class TestFeedbackCreate:
    """Tests for Feedback.create() factory method."""

    def test_create_with_corrections_and_suggestions(self, sample_correction):
        """Should create feedback with generated UUID and timestamp."""
        corrections = [sample_correction]
        suggestions = ["Try using more varied vocabulary"]

        feedback = Feedback.create(corrections=corrections, suggestions=suggestions)

        assert isinstance(feedback.id, UUID)
        assert feedback.corrections == corrections
        assert feedback.suggestions == suggestions
        assert isinstance(feedback.created_at, datetime)
        assert feedback.created_at.tzinfo == UTC
        assert feedback.user_rating is None
        assert feedback.user_comment is None

    def test_create_with_empty_lists(self):
        """Should allow empty corrections and suggestions."""
        feedback = Feedback.create(corrections=[], suggestions=[])
        assert feedback.corrections == []
        assert feedback.suggestions == []

    def test_create_with_multiple_correction_types(self):
        """Should handle multiple correction types."""
        corrections = [
            Correction(
                original="good",
                corrected="excellent",
                explanation="More precise",
                correction_type=CorrectionType.VOCABULARY,
            ),
            Correction(
                original="I goed",
                corrected="I went",
                explanation="Irregular verb",
                correction_type=CorrectionType.GRAMMAR,
            ),
            Correction(
                original="How do you do",
                corrected="How are you",
                explanation="More natural",
                correction_type=CorrectionType.PHRASING,
            ),
        ]
        feedback = Feedback.create(corrections=corrections, suggestions=[])
        assert len(feedback.corrections) == 3


class TestFeedbackReconstitute:
    """Tests for Feedback.reconstitute() loader method."""

    def test_reconstitute_with_all_fields(self, sample_correction):
        """Should reconstruct feedback with rating and comment."""
        feedback_id = uuid4()
        created = datetime(2025, 1, 15, 11, 0, tzinfo=UTC)

        feedback = Feedback.reconstitute(
            id=feedback_id,
            corrections=[sample_correction],
            suggestions=["Practice more"],
            created_at=created,
            user_rating=False,
            user_comment="Too complex",
        )

        assert feedback.id == feedback_id
        assert feedback.corrections == [sample_correction]
        assert feedback.created_at == created
        assert feedback.user_rating is False
        assert feedback.user_comment == "Too complex"

    def test_reconstitute_with_minimal_fields(self):
        """Should reconstruct with only required fields."""
        feedback = Feedback.reconstitute(
            id=uuid4(),
            corrections=[],
            suggestions=[],
            created_at=datetime.now(UTC),
        )

        assert feedback.user_rating is None
        assert feedback.user_comment is None


class TestFeedbackRate:
    """Tests for Feedback.rate() method."""

    def test_rate_helpful_clears_comment(self):
        """Should set positive rating and clear any previous comment."""
        feedback = Feedback.create(corrections=[], suggestions=[])
        feedback.user_comment = "Previous negative comment"

        feedback.rate(rating=True)

        assert feedback.user_rating is True
        assert feedback.user_comment is None

    def test_rate_not_helpful_with_comment(self):
        """Should set negative rating with comment."""
        feedback = Feedback.create(corrections=[], suggestions=[])

        feedback.rate(rating=False, comment="Not relevant to my needs")

        assert feedback.user_rating is False
        assert feedback.user_comment == "Not relevant to my needs"

    def test_rate_not_helpful_without_comment(self):
        """Should set negative rating without requiring comment."""
        feedback = Feedback.create(corrections=[], suggestions=[])

        feedback.rate(rating=False)

        assert feedback.user_rating is False
        assert feedback.user_comment is None

    def test_rate_can_change_rating(self):
        """Should allow changing rating from negative to positive."""
        feedback = Feedback.create(corrections=[], suggestions=[])
        feedback.rate(rating=False, comment="Initially bad")

        feedback.rate(rating=True)

        assert feedback.user_rating is True
        assert feedback.user_comment is None

    def test_rate_helpful_with_comment_ignores_comment(self):
        """Should ignore comment when rating is helpful."""
        feedback = Feedback.create(corrections=[], suggestions=[])

        feedback.rate(rating=True, comment="This should be ignored")

        assert feedback.user_rating is True
        assert feedback.user_comment is None

    def test_rate_updates_comment_when_rating_remains_false(self):
        """Should update comment when rating remains False but comment changes."""
        feedback = Feedback.create(corrections=[], suggestions=[])
        feedback.rate(rating=False, comment="Initial comment")

        feedback.rate(rating=False, comment="Updated comment")

        assert feedback.user_rating is False
        assert feedback.user_comment == "Updated comment"
