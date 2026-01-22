"""
LLM Summary Generator adapter.

Implements the SummaryProvider port using LLM clients.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from src.core.entities.conversation import Conversation
from src.core.entities.conversation_summary import ConversationSummary
from src.core.entities.message import MessageRole
from src.core.exceptions import SummaryGenerationError
from src.infrastructure.adapters.llm.clients.base import BaseLLMClient, LLMMessage

if TYPE_CHECKING:
    pass


SUMMARY_SYSTEM_PROMPT = """You are a language learning coach reviewing a conversation session.
Analyze the user's messages and provide constructive feedback on their language skills.

Always respond in valid JSON format with this structure:
{
    "fluency_score": <integer 0-100>,
    "strengths": ["strength 1", "strength 2"],
    "weaknesses": ["area to improve 1", "area to improve 2"],
    "overall_remarks": "Overall assessment and recommendations"
}

Be encouraging but honest. Focus on:
- Grammar accuracy
- Vocabulary usage
- Natural expression
- Communication effectiveness"""


def _build_summary_prompt(conversation: Conversation) -> str:
    """Build the summary analysis prompt with conversation content."""
    user_messages = [
        msg.content for msg in conversation.messages if msg.role == MessageRole.USER
    ]

    if not user_messages:
        return "No user messages to analyze."

    messages_text = "\n".join(f"- {msg}" for msg in user_messages)

    return f"""Please analyze the following user messages from a language learning conversation:

Topic: {conversation.context_topic}

User Messages:
{messages_text}

Provide a summary of the user's language performance."""


class LLMSummaryGenerator:
    """
    SummaryProvider implementation using LLM clients.

    Wraps any LLM client to generate conversation summaries.
    Implements the SummaryProvider protocol from core.ports.

    Uses JSON mode for structured output when available.
    """

    def __init__(self, client: BaseLLMClient) -> None:
        """
        Initialize with an LLM client.

        Args:
            client: The LLM client to use for summary generation.
        """
        self._client = client

    @property
    def model(self) -> str:
        """Get the model name (for debugging/logging)."""
        return self._client.model

    async def create_summary(self, conversation: Conversation) -> ConversationSummary:
        """
        Create an end-of-session summary for a conversation.

        Args:
            conversation: The completed conversation to summarize.

        Returns:
            ConversationSummary with fluency score and remarks.

        Raises:
            SummaryGenerationError: If summary generation fails.
        """
        messages = [
            LLMMessage(role="system", content=SUMMARY_SYSTEM_PROMPT),
            LLMMessage(role="user", content=_build_summary_prompt(conversation)),
        ]

        try:
            response = await self._client.complete(
                messages,
                temperature=0.5,  # Balanced for consistent but varied feedback
                json_mode=True,
            )

            # Parse JSON response
            try:
                data = json.loads(response.content)
            except json.JSONDecodeError as e:
                raise SummaryGenerationError(f"Invalid JSON response: {e}") from e

            return self._parse_summary(data)

        except SummaryGenerationError:
            raise
        except Exception as exc:
            raise SummaryGenerationError(f"Summary generation failed: {exc}") from exc

    def _parse_summary(self, data: dict[str, Any]) -> ConversationSummary:
        """Parse JSON response into ConversationSummary entity."""
        fluency_score = data.get("fluency_score", 50)

        # Ensure fluency_score is an integer in valid range
        if isinstance(fluency_score, (int, float)):
            fluency_score = max(0, min(100, int(fluency_score)))
        else:
            fluency_score = 50

        strengths = data.get("strengths", [])
        if not isinstance(strengths, list):
            strengths = []
        strengths = [str(s) for s in strengths if s]

        weaknesses = data.get("weaknesses", [])
        if not isinstance(weaknesses, list):
            weaknesses = []
        weaknesses = [str(w) for w in weaknesses if w]

        overall_remarks = str(data.get("overall_remarks", ""))

        return ConversationSummary.create(
            fluency_score=fluency_score,
            strengths=strengths,
            weaknesses=weaknesses,
            overall_remarks=overall_remarks,
        )
