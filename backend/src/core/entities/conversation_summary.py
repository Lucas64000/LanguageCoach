"""
ConversationSummary entity for end-of-session feedback.

Factory method .create() validates invariants.
Reconstitute method .reconstitute() for persistence loading (no validation).

ZERO external imports - pure Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.exceptions import InvalidFeedbackError


@dataclass
class ConversationSummary:
    """
    Summary generated when a conversation is completed.

    Provides overall assessment of the user's language performance.

    Attributes:
        id: Unique identifier for this summary.
        fluency_score: Overall fluency score (0-100).
        strengths: List of areas where user performed well.
        weaknesses: List of areas needing improvement.
        overall_remarks: General summary and recommendations.
        created_at: When the summary was generated.
    """

    id: UUID
    fluency_score: int
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    overall_remarks: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        fluency_score: int,
        strengths: list[str],
        weaknesses: list[str],
        overall_remarks: str,
    ) -> ConversationSummary:
        """
        Factory method for creating NEW summaries with validation.

        Args:
            fluency_score: Overall fluency score (0-100).
            strengths: List of strengths identified.
            weaknesses: List of weaknesses identified.
            overall_remarks: General summary text.

        Returns:
            A new ConversationSummary instance.

        Raises:
            InvalidFeedbackError: If fluency_score is out of range.
        """
        if not 0 <= fluency_score <= 100:
            raise InvalidFeedbackError(
                f"Fluency score must be between 0 and 100, got {fluency_score}"
            )

        return cls(
            id=uuid4(),
            fluency_score=fluency_score,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_remarks=overall_remarks,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        id: UUID,
        fluency_score: int,
        strengths: list[str],
        weaknesses: list[str],
        overall_remarks: str,
        created_at: datetime,
    ) -> ConversationSummary:
        """
        Loader method for reconstructing from persistence (NO validation).

        Used by repositories when loading from database. Trusts data integrity.

        Args:
            id: The summary's unique identifier.
            fluency_score: Overall fluency score.
            strengths: List of strengths.
            weaknesses: List of weaknesses.
            overall_remarks: General summary text.
            created_at: When the summary was created.

        Returns:
            A reconstituted ConversationSummary instance.
        """
        return cls(
            id=id,
            fluency_score=fluency_score,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_remarks=overall_remarks,
            created_at=created_at,
        )
