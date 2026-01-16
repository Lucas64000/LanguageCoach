"""
Application DTOs - Use Case DTOs only.

These are dataclass-based DTOs for use case input/output.
API DTOs (Pydantic) are in infrastructure/api/schemas/.
"""

from src.application.dtos.use_case_dtos import (
    ConversationDetailOutput,
    ConversationOutput,
    ConversationStatusOutput,
    CorrectionOutput,
    CreateConversationInput,
    FeedbackOutput,
    MessageOutput,
    RateFeedbackInput,
    RequestFeedbackInput,
    SendMessageInput,
    SendMessageOutput,
    SynthesisOutput,
    SynthesizeInput,
    TranscribeInput,
    TranscriptionOutput,
    ConversationSummaryOutput,
)

__all__ = [
    # Conversation
    "ConversationDetailOutput",
    "ConversationOutput",
    "ConversationStatusOutput",
    "CreateConversationInput",
    # Message
    "MessageOutput",
    "SendMessageInput",
    "SendMessageOutput",
    # Feedback
    "CorrectionOutput",
    "FeedbackOutput",
    "RateFeedbackInput",
    "RequestFeedbackInput",
    # Speech
    "SynthesisOutput",
    "SynthesizeInput",
    "TranscribeInput",
    "TranscriptionOutput",
    # Summary
    "ConversationSummaryOutput",
]
