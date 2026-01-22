"""Tests for OpenAI LLM Client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.exceptions import PartnerConnectionError, PartnerResponseError
from src.infrastructure.adapters.llm.clients.base import LLMMessage
from src.infrastructure.adapters.llm.clients.openai_client import OpenAIClient


@pytest.fixture
def mock_openai_async_client():
    """Mock AsyncOpenAI client."""
    mock_client = MagicMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock()
    return mock_client


@pytest.fixture
def openai_client(mock_openai_async_client):
    """OpenAI client with mocked underlying client."""
    client = OpenAIClient.__new__(OpenAIClient)
    client.model = "gpt-4o-mini"
    client._client = mock_openai_async_client
    return client


@pytest.fixture
def sample_messages():
    """Sample LLM messages."""
    return [
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="Hello!"),
    ]


class TestOpenAIClientComplete:
    """Tests for OpenAIClient.complete method."""

    @pytest.mark.asyncio
    async def test_complete_success(self, openai_client, mock_openai_async_client, sample_messages):
        """Successful completion returns LLMResponse."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello there!"))]

        mock_openai_async_client.chat.completions.create.return_value = mock_response

        response = await openai_client.complete(sample_messages)

        assert response.content == "Hello there!"
        assert response.model == "gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_complete_with_json_mode(self, openai_client, mock_openai_async_client, sample_messages):
        """JSON mode sets response_format."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"key": "value"}'))]

        mock_openai_async_client.chat.completions.create.return_value = mock_response

        response = await openai_client.complete(sample_messages, json_mode=True)

        call_kwargs = mock_openai_async_client.chat.completions.create.call_args[1]
        assert call_kwargs["response_format"] == {"type": "json_object"}
        assert response.content == '{"key": "value"}'

    @pytest.mark.asyncio
    async def test_complete_connection_error(self, openai_client, mock_openai_async_client, sample_messages):
        """Connection errors raise PartnerConnectionError."""
        mock_openai_async_client.chat.completions.create.side_effect = Exception("connection failed")

        with pytest.raises(PartnerConnectionError, match="Cannot connect"):
            await openai_client.complete(sample_messages)

    @pytest.mark.asyncio
    async def test_complete_timeout_error(self, openai_client, mock_openai_async_client, sample_messages):
        """Timeout errors raise PartnerConnectionError."""
        mock_openai_async_client.chat.completions.create.side_effect = Exception("timeout occurred")

        with pytest.raises(PartnerConnectionError, match="Cannot connect"):
            await openai_client.complete(sample_messages)

    @pytest.mark.asyncio
    async def test_complete_generic_error(self, openai_client, mock_openai_async_client, sample_messages):
        """Generic errors raise PartnerResponseError."""
        mock_openai_async_client.chat.completions.create.side_effect = Exception("API error")

        with pytest.raises(PartnerResponseError, match="OpenAI API error"):
            await openai_client.complete(sample_messages)


class TestOpenAIClientCompleteStream:
    """Tests for OpenAIClient.complete_stream method."""

    @pytest.mark.asyncio
    async def test_complete_stream_success(self, openai_client, mock_openai_async_client, sample_messages):
        """Successful streaming yields tokens."""
        chunk1 = MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))])
        chunk2 = MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))])

        async def mock_stream():
            yield chunk1
            yield chunk2

        mock_openai_async_client.chat.completions.create.return_value = mock_stream()

        chunks = []
        async for chunk in openai_client.complete_stream(sample_messages):
            chunks.append(chunk)

        assert chunks == ["Hello", " world"]

    @pytest.mark.asyncio
    async def test_complete_stream_skips_empty_content(self, openai_client, mock_openai_async_client, sample_messages):
        """Stream skips chunks with None content."""
        chunk1 = MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))])
        chunk2 = MagicMock(choices=[MagicMock(delta=MagicMock(content=None))])
        chunk3 = MagicMock(choices=[MagicMock(delta=MagicMock(content="world"))])

        async def mock_stream():
            yield chunk1
            yield chunk2
            yield chunk3

        mock_openai_async_client.chat.completions.create.return_value = mock_stream()

        chunks = []
        async for chunk in openai_client.complete_stream(sample_messages):
            chunks.append(chunk)

        assert chunks == ["Hello", "world"]

    @pytest.mark.asyncio
    async def test_complete_stream_connection_error(self, openai_client, mock_openai_async_client, sample_messages):
        """Connection errors during streaming raise PartnerConnectionError."""
        mock_openai_async_client.chat.completions.create.side_effect = Exception("connection failed")

        with pytest.raises(PartnerConnectionError, match="Cannot connect"):
            async for _ in openai_client.complete_stream(sample_messages):
                pass


class TestOpenAIClientInit:
    """Tests for OpenAIClient initialization."""

    def test_init_with_api_key(self):
        """Initialization with API key creates client."""
        with patch("src.infrastructure.adapters.llm.clients.openai_client.AsyncOpenAI") as mock_cls:
            client = OpenAIClient(api_key="sk-test", model="gpt-4o")

            mock_cls.assert_called_once_with(api_key="sk-test")
            assert client.model == "gpt-4o"
            assert client.provider_id == "openai"

    def test_init_with_custom_client(self):
        """Initialization with custom client uses it."""
        mock_client = MagicMock()
        client = OpenAIClient(api_key="sk-test", model="gpt-4o", client=mock_client)

        assert client._client is mock_client
