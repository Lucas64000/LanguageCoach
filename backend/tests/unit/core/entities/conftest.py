
import pytest

from src.core.entities.conversation import Conversation
from src.core.value_objects import Correction, CorrectionType, ConversationTone, ConversationStatus
from src.core.entities.feedback import Feedback
from src.core.entities.message import Message, MessageRole


@pytest.fixture
def sample_correction():
    """Reusable correction for tests."""
    return Correction(
        original="I go to school yesterday",
        corrected="I went to school yesterday",
        explanation="Use past tense 'went' for past actions",
        correction_type=CorrectionType.GRAMMAR,
    )


@pytest.fixture
def sample_corrections(sample_correction):
    """List of sample corrections."""
    return [
        sample_correction,
        Correction(
            original="big house",
            corrected="large mansion",
            explanation="More sophisticated vocabulary",
            correction_type=CorrectionType.VOCABULARY,
        ),
    ]


@pytest.fixture
def sample_feedback(sample_corrections):
    """Reusable feedback instance."""
    return Feedback.create(
        corrections=sample_corrections,
        suggestions=["Try using more varied vocabulary", "Practice past tense"],
    )


@pytest.fixture
def active_conversation():
    """Reusable active conversation."""
    return Conversation.create(
        context_topic="Job interview practice",
        tone=ConversationTone.FRIENDLY,
    )


@pytest.fixture
def conversation_with_messages(active_conversation):
    """Conversation with some messages already added."""
    active_conversation.add_message("Hello coach", MessageRole.USER)
    active_conversation.add_message("Hi! How can I help?", MessageRole.COACH)
    active_conversation.add_message("I need interview tips", MessageRole.USER)
    return active_conversation
