"""
Core domain layer - NO external imports allowed.

Public API for the core domain:
- Entities: Conversation, Message, Feedback
- Ports: Protocol interfaces for infrastructure
- Value Objects: Immutable domain concepts
- Exceptions: Domain-specific errors
"""

from src.core.entities import Conversation, Feedback, Message, MessageRole
from src.core.exceptions import (
    ConversationNotFoundError,
    DomainException,
    FeedbackAnalysisError,
    FeedbackNotFoundError,
    InvalidContextError,
    InvalidConversationStateError,
    InvalidMessageContentError,
    MessageNotFoundError,
    PartnerConnectionError,
    PartnerResponseError,
    SynthesisError,
    TranscriptionError,
)
from src.core.ports import (
    ConversationPartner,
    ConversationRepository,
    FeedbackProvider,
    SpeechRecognizer,
    SpeechSynthesizer,
)
from src.core.value_objects import (
    ConversationStatus,
    ConversationTone,
    Correction,
    CorrectionType,
    TranscriptionResult,
)

__all__ = [
    # Entities
    "Conversation",
    "Feedback",
    "Message",
    "MessageRole",
    # Ports
    "ConversationPartner",
    "ConversationRepository",
    "FeedbackProvider",
    "SpeechRecognizer",
    "SpeechSynthesizer",
    # Value Objects
    "ConversationStatus",
    "ConversationTone",
    "Correction",
    "CorrectionType",
    "TranscriptionResult",
    # Exceptions
    "ConversationNotFoundError",
    "DomainException",
    "FeedbackAnalysisError",
    "FeedbackNotFoundError",
    "InvalidContextError",
    "InvalidConversationStateError",
    "InvalidMessageContentError",
    "MessageNotFoundError",
    "PartnerConnectionError",
    "PartnerResponseError",
    "SynthesisError",
    "TranscriptionError",
]
