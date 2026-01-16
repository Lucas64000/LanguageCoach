"""
Conversation Mapper.

Maps Conversation entities to Use Case DTOs.
"""

from src.application.dtos.use_case_dtos import (
    ConversationDetailOutput,
    ConversationOutput,
    ConversationStatusOutput,
    MessageOutput,
)
from src.application.mappers.feedback_mapper import FeedbackMapper
from src.core.entities.conversation import Conversation
from src.core.entities.message import Message


class ConversationMapper:
    """Mapper for Conversation entity to Use Case DTOs."""

    @staticmethod
    def to_output(entity: Conversation) -> ConversationOutput:
        """
        Map Conversation entity to summary DTO without messages.

        Args:
            entity: The Conversation domain entity.

        Returns:
            ConversationOutput DTO with summary information.
        """
        last_message = None
        if entity.messages:
            last_message = entity.messages[-1].content

        return ConversationOutput(
            id=entity.id,
            context_topic=entity.context_topic,
            tone=entity.tone.value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            message_count=len(entity.messages),
            last_message=last_message,
        )

    @staticmethod
    def to_detail_output(entity: Conversation) -> ConversationDetailOutput:
        """
        Map Conversation entity to detailed DTO with messages.

        Args:
            entity: The Conversation domain entity.

        Returns:
            ConversationDetailOutput DTO including all messages.
        """
        from src.application.mappers.message_mapper import MessageMapper

        messages = tuple(MessageMapper.to_output(m) for m in entity.messages)

        return ConversationDetailOutput(
            id=entity.id,
            context_topic=entity.context_topic,
            tone=entity.tone.value,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            messages=messages,
        )

    @staticmethod
    def to_status_output(entity: Conversation) -> ConversationStatusOutput:
        """
        Map Conversation entity to status DTO.

        Args:
            entity: The Conversation domain entity.

        Returns:
            ConversationStatusOutput DTO for status operations.
        """
        return ConversationStatusOutput(
            id=entity.id,
            status=entity.status.value,
        )
