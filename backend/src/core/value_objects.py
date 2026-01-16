"""
Core value objects

Value objects are immutable and compared by value, not identity.
"""

from dataclasses import dataclass
from enum import Enum


class CorrectionType(Enum):
    """Type of language correction in feedback."""

    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    PHRASING = "phrasing"


@dataclass(frozen=True)
class Correction:
    """
    A single correction within feedback.

    Value object - immutable and compared by value.
    """

    original: str
    corrected: str
    explanation: str
    correction_type: CorrectionType


class ConversationStatus(Enum):
    """Status of a conversation."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ConversationTone(Enum):
    """
    Predefined conversation tones for the language coach.

    Each tone adjusts the coaching style to match user preferences.
    """

    FORMAL = "formal"
    FRIENDLY = "friendly"
    ENCOURAGING = "encouraging"
    PATIENT = "patient"


@dataclass(frozen=True)
class TranscriptionResult:
    """
    Result of speech-to-text transcription.

    Value object - immutable and compared by value.
    """

    text: str
    confidence: float
    duration_seconds: float
