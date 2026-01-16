"""
Summary Mapper.

Maps ConversationSummary entities to Use Case DTOs.
"""

from src.application.dtos.use_case_dtos import ConversationSummaryOutput
from src.core.entities.conversation_summary import ConversationSummary


class SummaryMapper:
    """Maps ConversationSummary entity to output DTOs."""

    @staticmethod
    def to_output(summary: ConversationSummary) -> ConversationSummaryOutput:
        """
        Convert ConversationSummary entity to output DTO.

        Args:
            summary: The ConversationSummary entity.

        Returns:
            ConversationSummaryOutput DTO.
        """
        return ConversationSummaryOutput(
            id=summary.id,
            fluency_score=summary.fluency_score,
            strengths=tuple(summary.strengths),
            weaknesses=tuple(summary.weaknesses),
            overall_remarks=summary.overall_remarks,
            created_at=summary.created_at,
        )
