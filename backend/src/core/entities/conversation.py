"""
Conversation entity - Aggregate Root for the conversation domain.

Factory method .create() validates invariants.
Reconstitute method .reconstitute() for persistence loading (no validation).

ZERO external imports - pure Python standard library only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.core.entities.message import Message, MessageRole
from src.core.exceptions import InvalidContextError, InvalidConversationStateError
from src.core.value_objects import ConversationStatus, ConversationTone

if TYPE_CHECKING:
    from src.core.entities.conversation_summary import ConversationSummary


@dataclass
class Conversation:
    """
    A conversation session between user and coach.

    This is the Aggregate Root for conversations. It owns Message entities.

    Attributes:
        id: Unique identifier for this conversation.
        context_topic: The scenario/context for the conversation.
        messages: List of messages in this conversation.
        created_at: When the conversation was started.
        updated_at: When the conversation was last modified.
        status: Current status of the conversation.
        tone: The coaching tone for this conversation.
    """

    id: UUID
    context_topic: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: ConversationStatus = ConversationStatus.ACTIVE
    tone: ConversationTone = field(default=ConversationTone.FRIENDLY)
    summary: ConversationSummary | None = None

    @property
    def is_active(self) -> bool:
        return self.status == ConversationStatus.ACTIVE

    @property
    def is_archived(self) -> bool:
        return self.status == ConversationStatus.ARCHIVED

    @property
    def is_completed(self) -> bool:
        return self.status == ConversationStatus.COMPLETED

    @classmethod
    def create(
        cls,
        context_topic: str,
        tone: ConversationTone = ConversationTone.FRIENDLY,
    ) -> Conversation:
        """
        Factory method for creating NEW conversations with validation.

        Args:
            context_topic: The scenario/context for the conversation.
            tone: The coaching tone/style.

        Returns:
            A new Conversation instance.

        Raises:
            InvalidContextError: If context_topic is empty or whitespace-only.
        """
        if not context_topic or not context_topic.strip():
            raise InvalidContextError("Context topic cannot be empty")

        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            context_topic=context_topic.strip(),
            messages=[],
            created_at=now,
            updated_at=now,
            status=ConversationStatus.ACTIVE,
            tone=tone,
        )

    @classmethod
    def reconstitute(
        cls,
        id: UUID,
        context_topic: str,
        messages: list[Message],
        created_at: datetime,
        updated_at: datetime,
        status: ConversationStatus = ConversationStatus.ACTIVE,
        tone: ConversationTone = ConversationTone.FRIENDLY,
        summary: ConversationSummary | None = None,
    ) -> Conversation:
        """
        Loader method for reconstructing from persistence (NO validation).

        Used by repositories when loading from database. Trusts data integrity.

        Args:
            id: The conversation's unique identifier.
            context_topic: The conversation context.
            messages: List of messages in the conversation.
            created_at: When the conversation was created.
            updated_at: When the conversation was last modified.
            status: Current status of the conversation.
            tone: The coaching tone.
            summary: Optional conversation summary.

        Returns:
            A reconstituted Conversation instance.
        """
        return cls(
            id=id,
            context_topic=context_topic,
            messages=messages,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            tone=tone,
            summary=summary,
        )

    def archive(self) -> None:
        """
        Archive this conversation.

        Raises:
            InvalidConversationStateError: If already archived.
        """
        if self.status == ConversationStatus.ARCHIVED:
            raise InvalidConversationStateError("Conversation is already archived")
        if self.status == ConversationStatus.COMPLETED:
            raise InvalidConversationStateError(
                "Cannot archive a completed conversation"
            )
        self.status = ConversationStatus.ARCHIVED
        self._touch()

    def restore(self) -> None:
        """
        Restore this conversation to active status.

        Raises:
            InvalidConversationStateError: If already active.
        """
        if self.status == ConversationStatus.ACTIVE:
            raise InvalidConversationStateError("Conversation is already active")
        self.status = ConversationStatus.ACTIVE
        self._touch()

    def end(self) -> None:
        """Mark conversation as completed."""
        if self.status == ConversationStatus.COMPLETED:
            raise InvalidConversationStateError("Conversation is already completed")
        if self.status == ConversationStatus.ARCHIVED:
            raise InvalidConversationStateError(
                "Cannot complete an archived conversation"
            )
        self.status = ConversationStatus.COMPLETED
        self._touch()

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(UTC)

    def add_message(self, content: str, role: MessageRole) -> Message:
        """
        Create and add a message to this conversation.

        The Aggregate Root controls child entity creation (DDD pattern).

        Args:
            content: The text content of the message.
            role: Whether this message is from USER or COACH.

        Returns:
            The newly created Message.
        """
        message = Message.create(content=content, role=role)
        self.messages.append(message)
        self._touch()
        return message

    def attach_summary(self, summary: ConversationSummary) -> None:
        """
        Attach a summary to this conversation.

        Args:
            summary: The summary to attach.

        Raises:
            InvalidConversationStateError: If not completed or already has summary.
        """
        if self.status != ConversationStatus.COMPLETED:
            raise InvalidConversationStateError(
                "Can only attach summary to completed conversation"
            )
        if self.summary is not None:
            raise InvalidConversationStateError("Conversation already has a summary")
        self.summary = summary
        self._touch()
