"""
Feedback analysis prompts for feedback providers.

Contains prompts for language error analysis.
"""

FEEDBACK_SYSTEM_PROMPT = (
    "You are a language tutor analyzing student messages. Always respond in valid JSON."
)


FEEDBACK_ANALYSIS_PROMPT = """
You are a language tutor analyzing a student's message for errors.

Message: "<<MESSAGE>>"

Carefully analyze this message and identify ONLY actual errors in:
- Grammar (verb tenses, subject-verb agreement, word order, articles, etc.)
- Vocabulary (wrong word choice, inappropriate word for context)
- Phrasing (awkward or unnatural expressions)

Respond **ONLY** in valid JSON format (no markdown, no extra text):
{
  "corrections": [
    {
      "original": "the exact incorrect phrase from the message",
      "corrected": "the corrected version",
      "explanation": "brief explanation of the error",
      "type": "grammar"
    }
  ],
  "suggestions": ["optional tips for improvement"]
}

IMPORTANT RULES:
1. If the message has NO errors, return: {"corrections": [], "suggestions": []}
2. Only report REAL errors - don't correct things that are already correct
3. "type" must be exactly one of: "grammar", "vocabulary", or "phrasing"
4. "original" must be the EXACT text from the message
5. Keep explanations short and helpful
6. Do NOT invent errors where there are none

Examples:
- Message: "I go to school yesterday" → Correction needed (went, not go)
- Message: "I like apples" → NO correction needed (already perfect)
- Message: "He don't like it" → Correction needed (doesn't, not don't)
"""


def build_feedback_prompt(message_content: str) -> str:
    """
    Build the feedback analysis prompt with the message content.

    Args:
        message_content: The user message to analyze.

    Returns:
        The complete feedback prompt string.
    """
    return FEEDBACK_ANALYSIS_PROMPT.replace("<<MESSAGE>>", message_content)
