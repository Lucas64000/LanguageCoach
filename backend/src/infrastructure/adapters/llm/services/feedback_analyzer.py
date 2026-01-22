"""
LLM Feedback Analyzer adapter.

Implements the FeedbackProvider port using LLM clients.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from src.core.entities.feedback import Feedback
from src.core.entities.message import Message
from src.core.exceptions import FeedbackAnalysisError
from src.core.value_objects import Correction, CorrectionType
from src.infrastructure.adapters.llm.clients.base import BaseLLMClient, LLMMessage
from src.infrastructure.prompts import FEEDBACK_SYSTEM_PROMPT, build_feedback_prompt

if TYPE_CHECKING:
    pass


class LLMFeedbackAnalyzer:
    """
    FeedbackProvider implementation using LLM clients.

    Wraps any LLM client to provide language feedback analysis.
    Implements the FeedbackProvider protocol from core.ports.

    Uses JSON mode for structured output when available.
    """

    def __init__(self, client: BaseLLMClient) -> None:
        """
        Initialize with an LLM client.

        Args:
            client: The LLM client to use for analysis.
        """
        self._client = client

    @property
    def model(self) -> str:
        """Get the model name (for backwards compatibility)."""
        return self._client.model

    async def analyze_message(self, message: Message) -> Feedback:
        """
        Analyze a message and generate feedback.

        Args:
            message: The user message to analyze.

        Returns:
            Feedback containing corrections and suggestions.

        Raises:
            FeedbackAnalysisError: If analysis fails.
        """
        messages = [
            LLMMessage(role="system", content=FEEDBACK_SYSTEM_PROMPT),
            LLMMessage(role="user", content=build_feedback_prompt(message.content)),
        ]

        try:
            response = await self._client.complete(
                messages,
                temperature=0.3,  # Lower temperature for consistent analysis
                json_mode=True,
            )

            # Parse JSON response
            try:
                data = json.loads(response.content)
            except json.JSONDecodeError as e:
                raise FeedbackAnalysisError(f"Invalid JSON response: {e}") from e

            return self._parse_feedback(data)

        except FeedbackAnalysisError:
            raise
        except Exception as exc:
            raise FeedbackAnalysisError(f"Feedback analysis failed: {exc}") from exc

    def _parse_feedback(self, data: dict[str, Any]) -> Feedback:
        """Parse JSON response into Feedback entity."""
        corrections_data = data.get("corrections", [])
        corrections: list[Correction] = []

        for entry in corrections_data:
            correction_type = self._normalize_type(entry.get("type"))
            if (
                correction_type is None
                or not entry.get("original")
                or not entry.get("corrected")
            ):
                continue
            corrections.append(
                Correction(
                    original=entry["original"],
                    corrected=entry["corrected"],
                    explanation=entry.get("explanation", "").strip(),
                    correction_type=correction_type,
                )
            )

        suggestions = (
            list(data.get("suggestions", []))
            if isinstance(data.get("suggestions", []), list)
            else []
        )

        return Feedback.create(corrections=corrections, suggestions=suggestions)

    def _normalize_type(self, correction_type: Any) -> CorrectionType | None:
        """Normalize correction type string to enum."""
        if not isinstance(correction_type, str):
            return None

        type_lower = correction_type.lower().strip()
        mapping = {
            "grammar": CorrectionType.GRAMMAR,
            "vocabulary": CorrectionType.VOCABULARY,
            "phrasing": CorrectionType.PHRASING,
        }
        return mapping.get(type_lower)
