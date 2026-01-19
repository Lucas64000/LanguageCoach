"""
Feedback Use Cases.

Operations for requesting and rating feedback on messages.
All operations use DTOs for input and output.
"""

from src.application.dtos.use_case_dtos import (
    FeedbackOutput,
    RateFeedbackInput,
    RequestFeedbackInput,
)
from src.application.mappers import FeedbackMapper
from src.core.exceptions import FeedbackNotFoundError
from src.core.ports import ConversationRepository, FeedbackMetrics, FeedbackProvider


class FeedbackUseCases:
    """
    Use cases for feedback operations.

    Groups related feedback operations: request and rate.
    """

    def __init__(
        self,
        repository: ConversationRepository,
        feedback_provider: FeedbackProvider,
        metrics: FeedbackMetrics,
    ) -> None:
        """
        Initialize with dependencies.

        Args:
            repository: Port for conversation persistence.
            feedback_provider: Port for generating feedback.
            metrics: Port for recording feedback metrics.
        """
        self._repository = repository
        self._feedback_provider = feedback_provider
        self._metrics = metrics

    async def request(self, input_dto: RequestFeedbackInput) -> FeedbackOutput:
        """
        Request feedback on a specific message.

        Args:
            input_dto: Contains the message ID to analyze.

        Returns:
            Feedback DTO with corrections and suggestions.

        Raises:
            MessageNotFoundError: If no message with this ID exists.
            InvalidMessageContentError: If message is not a user message.
        """
        # Record feedback request metric
        self._metrics.record_request()

        # Get conversation containing the message
        conversation = await self._repository.get_by_message_id(input_dto.message_id)

        # Find the message in the conversation
        message = next(
            (m for m in conversation.messages if m.id == input_dto.message_id),
            None,
        )

        # Analyze message with feedback provider
        feedback = await self._feedback_provider.analyze_message(message)

        # Attach feedback to message
        message.attach_feedback(feedback)

        # Persist updated conversation
        await self._repository.save(conversation)

        return FeedbackMapper.to_output(feedback)

    async def rate(self, input_dto: RateFeedbackInput) -> FeedbackOutput:
        """
        Rate feedback on a message.

        Args:
            input_dto: Contains message ID, rating, and optional comment.

        Returns:
            Updated feedback DTO.

        Raises:
            MessageNotFoundError: If message not found.
            FeedbackNotFoundError: If message has no feedback.
        """
        conversation = await self._repository.get_by_message_id(input_dto.message_id)

        # Find the message
        message = next(
            (m for m in conversation.messages if m.id == input_dto.message_id),
            None,
        )

        # Check feedback exists
        if message is None or message.feedback is None:
            raise FeedbackNotFoundError(
                f"Feedback for message {input_dto.message_id} not found"
            )

        # Rate the feedback
        message.feedback.rate(rating=input_dto.rating, comment=input_dto.comment)

        # Record satisfaction metrics via port
        self._metrics.record_rating(helpful=input_dto.rating)
        self._metrics.record_satisfaction(1.0 if input_dto.rating else 0.0)

        # Save the conversation
        await self._repository.save(conversation)

        return FeedbackMapper.to_output(message.feedback)

