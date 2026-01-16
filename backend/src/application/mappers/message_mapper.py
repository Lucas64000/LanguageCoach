"""
Message Mapper.

Maps Message entities to Use Case DTOs.
"""

from src.application.dtos.use_case_dtos import MessageOutput
from src.application.mappers.feedback_mapper import FeedbackMapper
from src.core.entities.message import Message


class MessageMapper:
    """Mapper for Message entity to Use Case DTOs."""

    @staticmethod
    def to_output(entity: Message) -> MessageOutput:
        """Map Message entity to DTO.

        Args:
            entity: The Message domain entity.

        Returns:
            MessageOutput DTO.
        """
        feedback_dto = None
        if entity.feedback:
            feedback_dto = FeedbackMapper.to_output(entity.feedback)

        return MessageOutput(
            id=entity.id,
            content=entity.content,
            role=entity.role.value,
            created_at=entity.created_at,
            feedback=feedback_dto,
        )
