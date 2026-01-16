"""
Tests for SendMessage use case.

Tests orchestration behavior with mocked dependencies.
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.dtos.use_case_dtos import SendMessageInput, SendMessageOutput
from src.application.use_cases.send_message import SendMessage
from src.core.entities.conversation import Conversation
from src.core.entities.message import MessageRole
from src.core.exceptions import ConversationNotFoundError, InvalidConversationStateError


class TestSendMessage:
    """Tests for SendMessage use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock repository."""
        repo = AsyncMock()
        repo.save = AsyncMock(return_value=None)
        repo.get_active = AsyncMock()
        return repo

    @pytest.fixture
    def mock_partner(self) -> AsyncMock:
        """Create a mock conversation partner."""
        partner = AsyncMock()
        partner.generate_response = AsyncMock(return_value="Coach response")
        return partner

    @pytest.fixture
    def use_case(
        self, mock_repository: AsyncMock, mock_partner: AsyncMock
    ) -> SendMessage:
        """Create use case with mock dependencies."""
        return SendMessage(repository=mock_repository, partner=mock_partner)

    @pytest.fixture
    def conversation(self) -> Conversation:
        """Create a test conversation."""
        return Conversation.create(context_topic="coffee shop")

    async def test_sends_message_and_gets_response(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
        mock_partner: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify use case sends message and gets coach response."""
        mock_repository.get_active = AsyncMock(return_value=conversation)

        result = await use_case.execute(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Hello coach",
            )
        )

        assert isinstance(result, SendMessageOutput)
        assert result.user_message.content == "Hello coach"
        assert result.user_message.role == MessageRole.USER.value
        assert result.coach_message.content == "Coach response"
        assert result.coach_message.role == MessageRole.COACH.value

    async def test_calls_partner_with_context_and_messages(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
        mock_partner: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify partner is called with correct context and messages."""
        mock_repository.get_active = AsyncMock(return_value=conversation)

        await use_case.execute(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Bonjour",
            )
        )

        mock_partner.generate_response.assert_called_once()
        # Get the call args - can be positional or keyword
        call_args = mock_partner.generate_response.call_args
        # Try kwargs first, fall back to args
        if call_args.kwargs:
            context = call_args.kwargs["context"]
            messages = call_args.kwargs["messages"]
        else:
            context = call_args.args[0]
            messages = call_args.args[1]

        assert context == "coffee shop"
        assert messages[0].content == "Bonjour"

    async def test_saves_conversation_after_messages(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
        mock_partner: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify conversation is saved with both messages."""
        mock_repository.get_active = AsyncMock(return_value=conversation)

        await use_case.execute(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Test",
            )
        )

        mock_repository.save.assert_called_once_with(conversation)
        assert len(conversation.messages) == 2

    async def test_raises_error_when_conversation_not_found(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
    ) -> None:
        """Verify ConversationNotFoundError is raised for missing conversation."""
        fake_id = uuid4()
        mock_repository.get_active = AsyncMock(
            side_effect=ConversationNotFoundError(
                f"Conversation {fake_id} not found"
            )
        )

        with pytest.raises(ConversationNotFoundError) as exc_info:
            await use_case.execute(
                SendMessageInput(conversation_id=fake_id, content="Hello")
            )

        assert str(fake_id) in str(exc_info.value)

    async def test_raises_error_when_conversation_is_archived(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify InvalidConversationStateError is raised for archived conversation."""
        conversation.archive()  # Archive the conversation
        mock_repository.get_active = AsyncMock(
            side_effect=InvalidConversationStateError(
                "Cannot send messages to an archived conversation"
            )
        )

        with pytest.raises(InvalidConversationStateError) as exc_info:
            await use_case.execute(
                SendMessageInput(
                    conversation_id=conversation.id,
                    content="Hello",
                )
            )

        assert "archived" in str(exc_info.value).lower()

    async def test_raises_error_when_conversation_is_completed(
        self,
        use_case: SendMessage,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify InvalidConversationStateError is raised for completed conversation."""
        conversation.end()
        mock_repository.get_active = AsyncMock(
            side_effect=InvalidConversationStateError(
                "Cannot send messages to a completed conversation"
            )
        )

        with pytest.raises(InvalidConversationStateError) as exc_info:
            await use_case.execute(
                SendMessageInput(
                    conversation_id=conversation.id,
                    content="Hello",
                )
            )

        assert "completed" in str(exc_info.value).lower()

    async def test_execute_stream_raises_error_when_archived(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify execute_stream raises error for archived conversation."""
        conversation.archive()  # Archive the conversation
        mock_repository.get_active = AsyncMock(
            side_effect=InvalidConversationStateError(
                "Cannot send messages to an archived conversation"
            )
        )

        mock_partner = AsyncMock()
        use_case = SendMessage(repository=mock_repository, partner=mock_partner)

        with pytest.raises(InvalidConversationStateError) as exc_info:
            async for _ in use_case.execute_stream(
                SendMessageInput(
                    conversation_id=conversation.id,
                    content="Hello",
                )
            ):
                pass

        assert "archived" in str(exc_info.value).lower()

    async def test_execute_stream_raises_error_when_completed(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """execute_stream raises error for completed conversation."""
        conversation.end()
        mock_repository.get_active = AsyncMock(
            side_effect=InvalidConversationStateError(
                "Cannot send messages to a completed conversation"
            )
        )

        mock_partner = AsyncMock()
        use_case = SendMessage(repository=mock_repository, partner=mock_partner)

        with pytest.raises(InvalidConversationStateError) as exc_info:
            async for _ in use_case.execute_stream(
                SendMessageInput(
                    conversation_id=conversation.id,
                    content="Hello",
                )
            ):
                pass

        assert "completed" in str(exc_info.value).lower()

    async def test_execute_stream_yields_tokens(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify execute_stream yields tokens from partner."""
        # Mock streaming partner
        async def mock_stream(*args, **kwargs):
            for token in ["Hello", " ", "World"]:
                yield token

        mock_partner = AsyncMock()
        mock_partner.generate_response_stream = mock_stream

        use_case = SendMessage(repository=mock_repository, partner=mock_partner)
        mock_repository.get_active = AsyncMock(return_value=conversation)

        tokens: list[str] = []
        async for token in use_case.execute_stream(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Test message",
            )
        ):
            tokens.append(token)

        assert tokens == ["Hello", " ", "World"]

    async def test_execute_stream_saves_user_message_before_streaming(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify user message is added and persisted before streaming starts."""
        save_call_count = 0

        async def mock_stream(*args, **kwargs):
            # Check user message was added and saved when streaming starts
            nonlocal save_call_count
            assert len(conversation.messages) >= 1
            assert save_call_count >= 1  # save called before streaming
            yield "token"

        mock_partner = AsyncMock()
        mock_partner.generate_response_stream = mock_stream

        async def track_save(conv):
            nonlocal save_call_count
            save_call_count += 1

        use_case = SendMessage(repository=mock_repository, partner=mock_partner)
        mock_repository.get_active = AsyncMock(return_value=conversation)
        mock_repository.save = track_save

        async for _ in use_case.execute_stream(
            SendMessageInput(
                conversation_id=conversation.id,
                content="User message",
            )
        ):
            pass

        assert conversation.messages[0].content == "User message"

    async def test_execute_stream_persists_coach_message_after_completion(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify coach message is added and persisted after streaming completes."""
        async def mock_stream(*args, **kwargs):
            for token in ["Hello", " ", "World"]:
                yield token

        mock_partner = AsyncMock()
        mock_partner.generate_response_stream = mock_stream

        use_case = SendMessage(repository=mock_repository, partner=mock_partner)
        mock_repository.get_active = AsyncMock(return_value=conversation)
        mock_repository.save = AsyncMock(return_value=None)

        tokens: list[str] = []
        async for token in use_case.execute_stream(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Test",
            )
        ):
            tokens.append(token)

        # Verify coach message was added
        assert len(conversation.messages) == 2
        assert conversation.messages[1].content == "Hello World"

        # Verify save was called twice (user message + coach message)
        assert mock_repository.save.call_count == 2

    async def test_execute_stream_does_not_save_coach_on_stream_error(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify coach message is NOT saved when streaming fails mid-way.

        Anthropic-style error handling: user message is safe, no partial coach.
        This prevents duplicate messages on retry.
        """
        save_call_count = 0

        async def mock_stream_with_error(*args, **kwargs):
            yield "Hello"
            yield " "
            raise RuntimeError("Stream interrupted")

        mock_partner = AsyncMock()
        mock_partner.generate_response_stream = mock_stream_with_error

        async def track_save(conv):
            nonlocal save_call_count
            save_call_count += 1

        use_case = SendMessage(repository=mock_repository, partner=mock_partner)
        mock_repository.get_active = AsyncMock(return_value=conversation)
        mock_repository.save = track_save

        tokens: list[str] = []
        with pytest.raises(RuntimeError, match="Stream interrupted"):
            async for token in use_case.execute_stream(
                SendMessageInput(
                    conversation_id=conversation.id,
                    content="User message",
                )
            ):
                tokens.append(token)

        # User message was saved before streaming
        assert save_call_count == 1
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "User message"
        assert conversation.messages[0].role == MessageRole.USER

    async def test_execute_stream_user_message_safe_on_empty_response(
        self,
        mock_repository: AsyncMock,
        conversation: Conversation,
    ) -> None:
        """Verify user message is saved even if coach returns empty response."""
        async def mock_empty_stream(*args, **kwargs):
            return
            yield  # noqa: unreachable - makes this an async generator

        mock_partner = AsyncMock()
        mock_partner.generate_response_stream = mock_empty_stream

        use_case = SendMessage(repository=mock_repository, partner=mock_partner)
        mock_repository.get_active = AsyncMock(return_value=conversation)
        mock_repository.save = AsyncMock(return_value=None)

        async for _ in use_case.execute_stream(
            SendMessageInput(
                conversation_id=conversation.id,
                content="Test message",
            )
        ):
            pass

        # User message saved, no coach message (empty response)
        assert mock_repository.save.call_count == 1
        assert len(conversation.messages) == 1
        assert conversation.messages[0].content == "Test message"

