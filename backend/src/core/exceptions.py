"""Core domain exceptions - pure Python."""


class DomainException(Exception):
    """Base class for all domain exceptions."""

    pass


# --- Entity Invariant Violations ---


class InvalidContextError(DomainException):
    """Raised when a conversation context topic is invalid (empty or whitespace-only)."""

    pass


class InvalidMessageContentError(DomainException):
    """Raised when message content is invalid (empty or whitespace-only)."""

    pass


class InvalidConversationStateError(DomainException):
    """Raised when a conversation state transition is invalid."""

    pass


# --- Repository Not Found ---


class ConversationNotFoundError(DomainException):
    """Raised when a conversation is not found by its ID."""

    pass


class MessageNotFoundError(DomainException):
    """Raised when a message is not found by its ID."""

    pass


class FeedbackNotFoundError(DomainException):
    """Raised when feedback is not found for a message."""

    pass


class InvalidFeedbackError(DomainException):
    """Raised when feedback data is invalid (e.g., score out of range)."""

    pass


# --- ConversationPartner Port Failures ---


class PartnerConnectionError(DomainException):
    """Raised when connection to partner fails."""

    pass


class PartnerResponseError(DomainException):
    """Raised when partner returns an invalid or malformed response."""

    pass


# --- FeedbackProvider Port Failures ---


class FeedbackAnalysisError(DomainException):
    """Raised when the feedback provider cannot analyze a message."""

    pass


# --- Speech Ports Failures ---


class TranscriptionError(DomainException):
    """Raised when speech-to-text transcription fails."""

    pass


class SynthesisError(DomainException):
    """Raised when text-to-speech synthesis fails."""

    pass
