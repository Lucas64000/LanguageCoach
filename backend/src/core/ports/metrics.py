"""
Metrics port.

Port defines the contract for providing metrics.
Core layer must have ZERO external imports.
"""

from typing import Protocol


class FeedbackMetrics(Protocol):
    """Protocol for feedback-related metrics."""

    def record_request(self) -> None:
        """Record a feedback request."""
        ...

    def record_rating(self, helpful: bool) -> None:
        """
        Record a user rating for feedback.

        Args:
            helpful: Whether the feedback was helpful.
        """
        ...

    def record_satisfaction(self, score: float) -> None:
        """
        Record satisfaction score (0.0 to 1.0).

        Args:
            score: Satisfaction score.
        """
        ...
