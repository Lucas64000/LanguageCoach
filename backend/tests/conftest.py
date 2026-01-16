"""
Pytest configuration for backend tests.

Centralized fixtures for all test suites.
"""

import os
from unittest.mock import AsyncMock

import pytest

from src.core.entities.conversation import Conversation
from src.core.entities.conversation_summary import ConversationSummary
from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole
from src.core.value_objects import Correction, CorrectionType, ConversationTone


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Configure test environment before collection."""
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    os.environ.setdefault("FEEDBACK_PROVIDER", "mock")


# =============================================================================
# MOCK REPOSITORIES AND PROVIDERS
# =============================================================================


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Create mock ConversationRepository."""
    return AsyncMock()


@pytest.fixture
def mock_feedback_provider() -> AsyncMock:
    """Create mock FeedbackProvider."""
    return AsyncMock()


@pytest.fixture
def mock_partner() -> AsyncMock:
    """Create mock ConversationPartner."""
    partner = AsyncMock()
    partner.generate_response = AsyncMock(return_value="Coach response")
    return partner


@pytest.fixture
def mock_summary_provider() -> AsyncMock:
    """Create mock SummaryProvider."""
    return AsyncMock()


# =============================================================================
# DOMAIN VALUE OBJECTS
# =============================================================================


@pytest.fixture
def sample_correction() -> Correction:
    """Reusable correction for tests."""
    return Correction(
        original="I go yesterday",
        corrected="I went yesterday",
        explanation="Use past tense for past actions",
        correction_type=CorrectionType.GRAMMAR,
    )


@pytest.fixture
def sample_corrections(sample_correction: Correction) -> list[Correction]:
    """List of sample corrections with multiple types."""
    return [
        sample_correction,
        Correction(
            original="big house",
            corrected="large mansion",
            explanation="More sophisticated vocabulary",
            correction_type=CorrectionType.VOCABULARY,
        ),
    ]


# =============================================================================
# DOMAIN ENTITIES - SIMPLE
# =============================================================================


@pytest.fixture
def sample_feedback(sample_correction: Correction) -> Feedback:
    """Create sample feedback for testing."""
    return Feedback.create(
        corrections=[sample_correction],
        suggestions=["Try using more descriptive verbs", "Practice past tense"],
    )


@pytest.fixture
def sample_feedback_with_rating(sample_correction: Correction) -> Feedback:
    """Create feedback with user rating (not helpful, with comment)."""
    feedback = Feedback.create(
        corrections=[sample_correction],
        suggestions=["Keep practicing"],
    )
    # Note: comment is only stored when rating=False per Feedback.rate() logic
    feedback.rate(rating=False, comment="Could be clearer")
    return feedback


@pytest.fixture
def sample_summary() -> ConversationSummary:
    """Create sample conversation summary."""
    return ConversationSummary.create(
        fluency_score=75,
        strengths=["Good vocabulary", "Natural flow"],
        weaknesses=["Verb tenses", "Prepositions"],
        overall_remarks="Great progress! Keep practicing verb conjugations.",
    )


@pytest.fixture
def conversation() -> Conversation:
    """Create a basic test conversation."""
    return Conversation.create(context_topic="coffee shop")


@pytest.fixture
def active_conversation() -> Conversation:
    """Create an active conversation with friendly tone."""
    return Conversation.create(
        context_topic="Job interview practice",
        tone=ConversationTone.FRIENDLY,
    )


# =============================================================================
# DOMAIN ENTITIES - COMPOSED
# =============================================================================


@pytest.fixture
def sample_conversation() -> Conversation:
    """Create a conversation with messages for mapper tests."""
    conv = Conversation.create(context_topic="coffee shop")
    conv.add_message("Hello, I want coffee please", MessageRole.USER)
    conv.add_message("Of course! What type would you like?", MessageRole.COACH)
    return conv


@pytest.fixture
def conversation_with_messages(active_conversation: Conversation) -> Conversation:
    """Conversation with multiple messages already added."""
    active_conversation.add_message("Hello coach", MessageRole.USER)
    active_conversation.add_message("Hi! How can I help?", MessageRole.COACH)
    active_conversation.add_message("I need interview tips", MessageRole.USER)
    return active_conversation


@pytest.fixture
def sample_conversation_with_message() -> tuple[Conversation, Message]:
    """Create conversation with a user message."""
    conv = Conversation.create(context_topic="coffee_shop")
    msg = conv.add_message("I go to store yesterday", MessageRole.USER)
    return conv, msg


@pytest.fixture
def sample_conversation_with_feedback(
    sample_feedback: Feedback,
) -> tuple[Conversation, Message]:
    """Create conversation with a user message that has feedback."""
    conv = Conversation.create(context_topic="test")
    msg = conv.add_message("test", MessageRole.USER)
    msg.attach_feedback(sample_feedback)
    return conv, msg


@pytest.fixture
def sample_message_with_feedback(
    sample_feedback: Feedback,
) -> tuple[Conversation, Message]:
    """Create message with attached feedback."""
    conv = Conversation.create(context_topic="test")
    msg = conv.add_message("I go to store yesterday", MessageRole.USER)
    msg.attach_feedback(sample_feedback)
    return conv, msg
