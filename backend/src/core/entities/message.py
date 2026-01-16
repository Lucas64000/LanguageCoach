"""
Message entity for conversation domain.

Factory  method .create() validates invariants.
Reconstitute method .reconstitute() for persistence loading (no validation).

ZERO external imports - pure Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.core.exceptions import InvalidMessageContentError

if TYPE_CHECKING:
    from src.core.entities.feedback import Feedback


class MessageRole(Enum):
    """Role of the message sender in a conversation."""

    USER = "user"
    COACH = "coach"


@dataclass
class Message:
    """
    A single message within a conversation.

    Attributes:
        id: Unique identifier for this message.
        content: The text content of the message.
        role: Whether this message is from USER or COACH.
        created_at: When the message was created.
        feedback: Optional feedback attached to this message.
    """

    id: UUID
    content: str
    role: MessageRole
    created_at: datetime
    feedback: Feedback | None = None

    @classmethod
    def create(
        cls,
        content: str,
        role: MessageRole,
    ) -> Message:
        """
        Factory method for creating NEW messages with validation.

        Args:
            content: The text content of the message.
            role: Whether this message is from USER or COACH.

        Returns:
            A new Message instance with generated id and timestamp.

        Raises:
            InvalidMessageContentError: If content is empty or whitespace-only.
        """
        if not content or not content.strip():
            raise InvalidMessageContentError("Message content cannot be empty")

        return cls(
            id=uuid4(),
            content=content,
            role=role,
            created_at=datetime.now(UTC),
            feedback=None,
        )

    @classmethod
    def reconstitute(
        cls,
        id: UUID,
        content: str,
        role: MessageRole,
        created_at: datetime,
        feedback: Feedback | None = None,
    ) -> Message:
        """
        Loader method for reconstructing from persistence (NO validation).

        Used by repositories when loading from database. Trusts data integrity.

        Args:
            id: The message's unique identifier.
            content: The text content.
            role: The message role.
            created_at: When the message was created.
            feedback: Optional feedback attached.

        Returns:
            A reconstituted Message instance.
        """
        return cls(
            id=id,
            content=content,
            role=role,
            created_at=created_at,
            feedback=feedback,
        )
