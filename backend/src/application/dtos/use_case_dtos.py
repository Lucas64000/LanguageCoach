"""
Use Case DTOs - Input and Output structures for application layer.

These DTOs decouple the use cases from both the domain entities and the API layer.
Input DTOs: Carry data INTO use cases (commands/queries)
Output DTOs: Carry data OUT of use cases (results)

IMPORTANT: These are NOT Pydantic models - they are simple dataclasses.
Pydantic models live in the API DTOs (conversation.py, message.py) for HTTP serialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


# =============================================================================
# CONVERSATION LIFECYCLE DTOs
# =============================================================================


@dataclass(frozen=True)
class CreateConversationInput:
    """Input for creating a new conversation."""

    context_topic: str
    tone: str  # String representation of tone (e.g., "formal", "friendly")


@dataclass(frozen=True)
class ConversationOutput:
    """Output representing a conversation."""

    id: UUID
    context_topic: str
    tone: str
    status: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: str | None = None


@dataclass(frozen=True)
class ConversationStatusOutput:
    """Output for status change operations (archive/restore/end)."""

    id: UUID
    status: str


# =============================================================================
# MESSAGE DTOs
# =============================================================================


@dataclass(frozen=True)
class SendMessageInput:
    """Input for sending a message."""

    conversation_id: UUID
    content: str


@dataclass(frozen=True)
class MessageOutput:
    """Output representing a message."""

    id: UUID
    content: str
    role: str
    created_at: datetime
    feedback: FeedbackOutput | None = None


@dataclass(frozen=True)
class SendMessageOutput:
    """Output for send message operation."""

    user_message: MessageOutput
    coach_message: MessageOutput


# =============================================================================
# FEEDBACK DTOs
# =============================================================================


@dataclass(frozen=True)
class RequestFeedbackInput:
    """Input for requesting feedback on a message."""

    message_id: UUID


@dataclass(frozen=True)
class RateFeedbackInput:
    """Input for rating feedback."""

    message_id: UUID
    rating: bool  # True = helpful, False = not helpful
    comment: str | None = None


@dataclass(frozen=True)
class CorrectionOutput:
    """Output representing a single correction."""

    original: str
    corrected: str
    explanation: str
    correction_type: str  # "grammar", "vocabulary", "phrasing"


@dataclass(frozen=True)
class FeedbackOutput:
    """Output representing feedback."""

    id: UUID
    corrections: tuple[CorrectionOutput, ...] = field(default_factory=tuple)
    suggestions: tuple[str, ...] = field(default_factory=tuple)
    created_at: datetime | None = None
    user_rating: bool | None = None
    user_comment: str | None = None


# =============================================================================
# SPEECH DTOs
# =============================================================================


@dataclass(frozen=True)
class TranscribeInput:
    """Input for transcribing audio."""

    audio_bytes: bytes


@dataclass(frozen=True)
class TranscriptionOutput:
    """Output from transcription."""

    text: str
    confidence: float | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True)
class SynthesizeInput:
    """Input for synthesizing speech."""

    text: str


@dataclass(frozen=True)
class SynthesisOutput:
    """Output from speech synthesis."""

    audio_bytes: bytes
    format: str = "mp3"


# =============================================================================
# CONVERSATION SUMMARY DTOs
# =============================================================================


@dataclass(frozen=True)
class EndConversationInput:
    """Input for ending a conversation with optional summary generation."""

    conversation_id: UUID
    generate_summary: bool = True


@dataclass(frozen=True)
class ConversationSummaryOutput:
    """Output representing a conversation summary."""

    id: UUID
    fluency_score: int
    strengths: tuple[str, ...] = field(default_factory=tuple)
    weaknesses: tuple[str, ...] = field(default_factory=tuple)
    overall_remarks: str = ""
    created_at: datetime | None = None


# =============================================================================
# CONVERSATION DETAIL DTOs (for queries)
# =============================================================================


@dataclass(frozen=True)
class ConversationDetailOutput:
    """Output for detailed conversation with messages."""

    id: UUID
    context_topic: str
    tone: str
    status: str
    created_at: datetime
    updated_at: datetime
    messages: tuple[MessageOutput, ...] = field(default_factory=tuple)
    summary: ConversationSummaryOutput | None = None


