"""
FeedbackProvider port for language feedback analysis.

Port defines the contract for generating responses.
Core layer must have ZERO external imports.
"""

from typing import Protocol

from src.core.entities.feedback import Feedback
from src.core.entities.message import Message


class FeedbackProvider(Protocol):
    """
    Port for feedback analysis operations.

    Implementations must be in infrastructure layer.
    """

    async def analyze_message(self, message: Message) -> Feedback:
        """
        Analyze a message and generate feedback.

        Args:
            message: The user message to analyze.

        Returns:
            Feedback containing corrections and suggestions.
        """
        ...
