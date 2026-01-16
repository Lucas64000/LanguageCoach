"""
Feedback entity for language correction domain.

Factory method .create() validates invariants.
Reconstitute method .reconstitute() for persistence loading (no validation).

ZERO external imports - pure Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.core.value_objects import Correction


@dataclass
class Feedback:
    """
    Feedback on a user message containing corrections and suggestions.

    Attributes:
        id: Unique identifier for this feedback.
        corrections: List of specific corrections (grammar, vocabulary, phrasing).
        suggestions: General suggestions for improvement.
        created_at: When the feedback was generated.
        user_rating: User's rating of this feedback (True=helpful, False=not helpful, None=unrated).
        user_comment: Optional comment explaining why feedback was not helpful.
    """

    id: UUID
    corrections: list[Correction] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    user_rating: bool | None = None
    user_comment: str | None = None


    @classmethod
    def create(
        cls,
        corrections: list[Correction],
        suggestions: list[str],
    ) -> Feedback:
        """
        Factory method for creating NEW feedback with validation.

        Args:
            corrections: List of corrections to apply.
            suggestions: List of general suggestions.

        Returns:
            A new Feedback instance with generated id and timestamp.
        """
        return cls(
            id=uuid4(),
            corrections=corrections,
            suggestions=suggestions,
            created_at=datetime.now(UTC),
        )

    @classmethod
    def reconstitute(
        cls,
        id: UUID,
        corrections: list[Correction],
        suggestions: list[str],
        created_at: datetime,
        user_rating: bool | None = None,
        user_comment: str | None = None,
    ) -> Feedback:
        """
        Loader method for reconstructing from persistence (NO validation).

        Used by repositories when loading from database. Trusts data integrity.

        Args:
            id: The feedback's unique identifier.
            corrections: List of corrections.
            suggestions: List of suggestions.
            created_at: When the feedback was created.
            user_rating: User's rating (True=helpful, False=not helpful).
            user_comment: User's comment if not helpful.

        Returns:
            A reconstituted Feedback instance.
        """
        return cls(
            id=id,
            corrections=corrections,
            suggestions=suggestions,
            created_at=created_at,
            user_rating=user_rating,
            user_comment=user_comment,
        )

    def rate(self, rating: bool, comment: str | None = None) -> None:
        """
        Set user rating for this feedback.

        Args:
            rating: True if helpful, False if not helpful.
            comment: Optional comment if not helpful.
        """
        self.user_rating = rating
        if not rating and comment:
            self.user_comment = comment
        elif rating:
            self.user_comment = None

