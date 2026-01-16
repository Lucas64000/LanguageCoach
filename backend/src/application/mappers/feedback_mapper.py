"""
Feedback Mapper.

Maps Feedback entities to Use Case DTOs.
"""

from src.application.dtos.use_case_dtos import CorrectionOutput, FeedbackOutput
from src.core.entities.feedback import Feedback


class FeedbackMapper:
    """Mapper for Feedback entity to Use Case DTOs."""

    @staticmethod
    def to_output(feedback: Feedback) -> FeedbackOutput:
        """
        Map Feedback entity to Use Case DTO.

        Args:
            feedback: The Feedback entity.

        Returns:
            FeedbackOutput DTO (dataclass).
        """
        corrections = tuple(
            CorrectionOutput(
                original=c.original,
                corrected=c.corrected,
                explanation=c.explanation,
                correction_type=c.correction_type.value,
            )
            for c in feedback.corrections
        )

        return FeedbackOutput(
            id=feedback.id,
            corrections=corrections,
            suggestions=tuple(feedback.suggestions),
            created_at=feedback.created_at,
            user_rating=feedback.user_rating,
            user_comment=feedback.user_comment,
        )

