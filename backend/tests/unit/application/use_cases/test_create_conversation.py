"""
Tests for CreateConversation use case.

Tests orchestration behavior, not entity defaults.
"""

from unittest.mock import AsyncMock

import pytest

from src.application.dtos.use_case_dtos import CreateConversationInput
from src.application.use_cases.create_conversation import CreateConversation
from src.core.exceptions import InvalidContextError


class TestCreateConversation:
    """Tests for CreateConversation use case."""

    @pytest.fixture
    def mock_repository(self) -> AsyncMock:
        """Create a mock repository."""
        repo = AsyncMock()
        repo.save = AsyncMock(return_value=None)
        return repo

    @pytest.fixture
    def use_case(self, mock_repository: AsyncMock) -> CreateConversation:
        """Create use case with mock repository."""
        return CreateConversation(repository=mock_repository)

    async def test_creates_and_saves_conversation(
        self, use_case: CreateConversation, mock_repository: AsyncMock
    ) -> None:
        """Verify use case creates conversation and calls repository.save()."""
        input_dto = CreateConversationInput(
            context_topic="coffee shop",
            tone="friendly",
        )
        result = await use_case.execute(input_dto)

        assert result.context_topic == "coffee shop"
        assert result.tone == "friendly"
        mock_repository.save.assert_called_once()

    @pytest.mark.parametrize("invalid_topic", ["", "   "])
    async def test_raises_error_for_invalid_topic(
        self, use_case: CreateConversation, invalid_topic: str
    ) -> None:
        """Verify domain exception is raised for invalid topics."""
        input_dto = CreateConversationInput(
            context_topic=invalid_topic,
            tone="friendly",
        )
        with pytest.raises(InvalidContextError):
            await use_case.execute(input_dto)
