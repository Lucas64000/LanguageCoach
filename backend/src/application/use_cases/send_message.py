"""
SendMessage use case.

Orchestrates sending a message and receiving a coach response.
Uses DTOs for input and output.
"""

from collections.abc import AsyncIterator

from src.application.dtos.use_case_dtos import SendMessageInput, SendMessageOutput
from src.application.mappers import MessageMapper
from src.core.entities import MessageRole
from src.core.ports import ConversationPartner, ConversationRepository


class SendMessage:
    """
    Use case for sending a message and receiving a coach response.

    Orchestrates domain logic, partner interaction, and persistence.
    """

    def __init__(
        self,
        repository: ConversationRepository,
        partner: ConversationPartner,
    ) -> None:
        """
        Initialize with dependencies.

        Args:
            repository: Port for conversation persistence.
            partner: Port for generating responses.
        """
        self._repository = repository
        self._partner = partner

    async def execute(self, input_dto: SendMessageInput) -> SendMessageOutput:
        """
        Send a user message and get a coach response.

        Args:
            input_dto: Contains conversation_id and message content.

        Returns:
            DTO containing both user and coach message DTOs.
        """
        conversation = await self._repository.get_active(input_dto.conversation_id)

        # Add user message
        user_message = conversation.add_message(input_dto.content, MessageRole.USER)

        # Generate coach response with tone
        response_content = await self._partner.generate_response(
            context=conversation.context_topic,
            messages=conversation.messages,
            tone=conversation.tone,
        )

        # Add coach message
        coach_message = conversation.add_message(response_content, MessageRole.COACH)

        # Persist
        await self._repository.save(conversation)

        return SendMessageOutput(
            user_message=MessageMapper.to_output(user_message),
            coach_message=MessageMapper.to_output(coach_message),
        )

    async def execute_stream(
        self, input_dto: SendMessageInput
    ) -> AsyncIterator[str]:
        """
        Send a user message and stream the coach response.

        Persists user message immediately, then streams tokens.
        Coach message is persisted after streaming completes.

        Args:
            input_dto: Contains conversation_id and message content.

        Yields:
            Token strings as they are generated.
        """
        conversation = await self._repository.get_active(input_dto.conversation_id)

        # Add and persist user message before streaming
        _ = conversation.add_message(input_dto.content, MessageRole.USER)
        await self._repository.save(conversation)

        # Accumulate coach response during streaming
        full_response: list[str] = []

        async for token in self._partner.generate_response_stream(
            context=conversation.context_topic,
            messages=conversation.messages,
            tone=conversation.tone,
        ):
            full_response.append(token)
            yield token

        # Only persist coach message on successful completion
        coach_content = "".join(full_response)
        if coach_content:
            _ = conversation.add_message(coach_content, MessageRole.COACH)
            await self._repository.save(conversation)
