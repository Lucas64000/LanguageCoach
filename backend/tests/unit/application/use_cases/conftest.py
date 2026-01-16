"""
Pytest fixtures for application use case tests.

Centralized fixtures to avoid duplication across test files.
"""

from unittest.mock import AsyncMock

import pytest

from src.core.entities.conversation import Conversation
from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole
from src.core.entities.conversation_summary import ConversationSummary
from src.core.value_objects import Correction, CorrectionType


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
# DOMAIN ENTITIES
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
def sample_feedback(sample_correction) -> Feedback:
    """Create sample feedback for testing."""
    return Feedback.create(
        corrections=[sample_correction],
        suggestions=["Try using more descriptive verbs"],
    )


@pytest.fixture
def sample_summary() -> ConversationSummary:
    """Create sample conversation summary."""
    return ConversationSummary.create(
        fluency_score=75,
        strengths=["Good vocabulary"],
        weaknesses=["Verb tenses"],
        overall_remarks="Keep practicing!",
    )


@pytest.fixture
def conversation() -> Conversation:
    """Create a test conversation."""
    return Conversation.create(context_topic="coffee shop")


@pytest.fixture
def sample_conversation_with_message() -> tuple[Conversation, Message]:
    """Create conversation with a user message."""
    conv = Conversation.create(context_topic="coffee_shop")
    msg = conv.add_message("I go to store yesterday", MessageRole.USER)
    return conv, msg


@pytest.fixture
def sample_conversation_with_feedback(
    sample_feedback,
) -> tuple[Conversation, Message]:
    """Create conversation with a user message that has feedback."""
    conv = Conversation.create(context_topic="test")
    msg = conv.add_message("test", MessageRole.USER)
    msg.attach_feedback(sample_feedback)
    return conv, msg
