"""
CreateConversation use case.

Orchestrates the creation of a new conversation.
Uses DTOs for input and output.
"""

from src.application.dtos.use_case_dtos import (
    ConversationOutput,
    CreateConversationInput,
)
from src.application.mappers import ConversationMapper
from src.core.entities import Conversation
from src.core.ports import ConversationRepository
from src.core.value_objects import ConversationTone


class CreateConversation:
    """
    Use case for creating a new conversation.

    Orchestrates domain logic and repository interaction.
    """

    def __init__(self, repository: ConversationRepository) -> None:
        """
        Initialize with repository dependency.

        Args:
            repository: Port for persisting conversations.
        """
        self._repository = repository

    async def execute(self, input_dto: CreateConversationInput) -> ConversationOutput:
        """
        Create a new conversation with the given topic and tone.

        Args:
            input_dto: Contains context_topic and tone.

        Returns:
            DTO representing the newly created conversation.

        Raises:
            InvalidContextError: If context_topic is invalid.
            ValueError: If tone is invalid.
        """
        # Map string tone to domain enum
        tone = ConversationTone(input_dto.tone)

        # Create domain entity
        conversation = Conversation.create(
            context_topic=input_dto.context_topic,
            tone=tone,
        )

        # Persist
        await self._repository.save(conversation)

        # Return DTO via mapper
        return ConversationMapper.to_output(conversation)

