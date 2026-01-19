"""Core ports - Protocol interfaces for infrastructure adapters."""

from src.core.ports.conversation_partner import ConversationPartner
from src.core.ports.conversation_repository import ConversationRepository
from src.core.ports.feedback_provider import FeedbackProvider
from src.core.ports.metrics import FeedbackMetrics
from src.core.ports.speech import SpeechRecognizer, SpeechSynthesizer
from src.core.ports.summary_provider import SummaryProvider

__all__ = [
    "ConversationPartner",
    "ConversationRepository",
    "FeedbackMetrics",
    "FeedbackProvider",
    "SpeechRecognizer",
    "SpeechSynthesizer",
    "SummaryProvider",
]
