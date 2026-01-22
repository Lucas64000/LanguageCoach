"""
Ollama LLM Client - Low-level client for local Ollama server.

Provides reusable client for any adapter needing Ollama completions.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

import httpx

from src.core.exceptions import PartnerConnectionError, PartnerResponseError
from src.infrastructure.adapters.llm.clients.base import (
    BaseLLMClient,
    LLMMessage,
    LLMResponse,
)


class OllamaClient(BaseLLMClient):
    """
    Ollama API client for local LLM inference.

    Handles all Ollama API communication with proper error handling.
    Reusable across different services (ConversationPartner, FeedbackProvider, etc.).
    """

    provider_id = "ollama"

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        """
        Initialize the Ollama client.

        Args:
            model: Model to use for completions.
            base_url: Ollama server URL.
            timeout: Request timeout in seconds.
            client: Optional pre-configured client (for testing).
        """
        super().__init__(model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._external_client = client

    @asynccontextmanager
    async def _get_client(self):
        """Get HTTP client, managing lifecycle appropriately."""
        if self._external_client:
            yield self._external_client
        else:
            async with httpx.AsyncClient() as client:
                yield client

    async def complete(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        Generate a completion using Ollama API.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON-formatted output.

        Returns:
            LLMResponse with content.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        if json_mode:
            payload["format"] = "json"

        try:
            async with self._get_client() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()

        except httpx.TimeoutException as e:
            raise PartnerConnectionError(
                f"Timeout connecting to Ollama at {self.base_url}: {e}"
            ) from e
        except httpx.ConnectError as e:
            raise PartnerConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?"
            ) from e
        except httpx.HTTPStatusError as e:
            raise PartnerResponseError(
                f"Ollama returned error status {e.response.status_code}: {e.response.text}"
            ) from e
        except httpx.RequestError as e:
            raise PartnerConnectionError(
                f"Request error while contacting Ollama: {e}"
            ) from e

        try:
            data = response.json()
            content = data["message"]["content"]
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            raise PartnerResponseError(
                f"Invalid response format from Ollama: {e}"
            ) from e

        return LLMResponse(
            content=content,
            model=self.model,
            raw_response=data,
        )

    async def complete_stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """
        Generate a streaming completion using Ollama API.

        Args:
            messages: List of messages forming the conversation.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Yields:
            Token strings as they arrive.

        Raises:
            PartnerConnectionError: If connection fails.
            PartnerResponseError: If API returns error.
        """
        ollama_messages = [{"role": m.role, "content": m.content} for m in messages]

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        try:
            async with (
                self._get_client() as client,
                client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout,
                ) as response,
            ):
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")

                        if content:
                            yield content

                        if data.get("done", False):
                            break

                    except json.JSONDecodeError:
                        continue

        except httpx.TimeoutException as e:
            raise PartnerConnectionError(
                f"Timeout connecting to Ollama at {self.base_url}: {e}"
            ) from e
        except httpx.ConnectError as e:
            raise PartnerConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. Is Ollama running?"
            ) from e
        except httpx.HTTPStatusError as e:
            raise PartnerResponseError(
                f"Ollama returned error status {e.response.status_code}"
            ) from e
        except httpx.RequestError as e:
            raise PartnerConnectionError(
                f"Request error while contacting Ollama: {e}"
            ) from e
