"""
Application Use Cases.

Grouped by domain concern:
- conversation_lifecycle: Archive, Restore, End, Delete
- conversation_queries: Get, List
- create_conversation: Create new conversation
- create_summary: Create conversation summary
- send_message: Send message and receive response
- feedback: Request and Rate feedback
- speech: Transcribe and Synthesize
"""

from src.application.use_cases.conversation_lifecycle import ChangeConversationStatus
from src.application.use_cases.conversation_queries import ConversationQueries
from src.application.use_cases.create_conversation import CreateConversation
from src.application.use_cases.create_summary import CreateSummary
from src.application.use_cases.feedback import FeedbackUseCases
from src.application.use_cases.send_message import SendMessage
from src.application.use_cases.speech import SpeechUseCases

__all__ = [
    "ChangeConversationStatus",
    "ConversationQueries",
    "CreateConversation",
    "FeedbackUseCases",
    "CreateSummary",
    "SendMessage",
    "SpeechUseCases",
]
