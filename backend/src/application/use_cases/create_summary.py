"""
CreateSummary Use Case.

Creates an end-of-session summary for a completed conversation.
"""

from src.application.dtos.use_case_dtos import (
    ConversationSummaryOutput,
    CreateSummaryInput,
)
from src.application.mappers import SummaryMapper
from src.core.exceptions import InvalidConversationStateError
from src.core.ports import ConversationRepository, SummaryProvider


class CreateSummary:
    """
    Use case for generating conversation summaries.

    Called when a user completes a conversation to provide
    overall feedback on their language performance.
    """

    def __init__(
        self,
        repository: ConversationRepository,
        summary_provider: SummaryProvider,
    ) -> None:
        """
        Initialize with dependencies.

        Args:
            repository: Port for conversation persistence.
            summary_provider: Port for generating summaries via LLM.
        """
        self._repository = repository
        self._summary_provider = summary_provider

    async def execute(self, input_dto: CreateSummaryInput) -> ConversationSummaryOutput:
        """
        Create a summary for a completed conversation.

        Args:
            input_dto: Contains the conversation ID to summarize.

        Returns:
            ConversationSummaryOutput with fluency score and remarks.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
            InvalidConversationStateError: If conversation is not completed
                or has no messages.
        """
        conversation = await self._repository.get(input_dto.conversation_id)

        # Validate conversation state
        if not conversation.is_completed:
            raise InvalidConversationStateError(
                f"Conversation {input_dto.conversation_id} must be completed to create summary"
            )

        if not conversation.messages:
            raise InvalidConversationStateError(
                f"Conversation {input_dto.conversation_id} has no messages to summarize"
            )

        # Create summary via provider
        summary = await self._summary_provider.create_summary(conversation)

        return SummaryMapper.to_output(summary)
