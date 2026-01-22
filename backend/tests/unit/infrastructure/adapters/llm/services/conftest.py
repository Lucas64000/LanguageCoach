"""Shared fixtures for LLM services tests."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_client():
    """
    Mock LLM client for service tests.

    Pre-configured with async complete and complete_stream methods.
    """
    client = MagicMock()
    client.provider_id = "mock"
    client.model = "mock-model"
    client.complete = AsyncMock()
    client.complete_stream = AsyncMock()
    return client
