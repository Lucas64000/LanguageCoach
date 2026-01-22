"""Tests for Provider Registry."""

from unittest.mock import MagicMock

import pytest

from src.infrastructure.adapters.llm.models import ModelInfo
from src.infrastructure.adapters.llm.registry import (
    ProviderRegistry,
    register_provider,
)
from src.infrastructure.adapters.llm.registry import (
    registry as global_registry,
)


@pytest.fixture
def registry():
    """Fresh registry for each test."""
    reg = ProviderRegistry()
    yield reg
    reg.clear()


@pytest.fixture
def mock_provider():
    """Mock provider class."""

    class MockProvider:
        provider_id = "mock"
        provider_name = "Mock"

        @staticmethod
        def is_available(settings):
            return bool(settings.api_key)

        @staticmethod
        def list_models():
            return [ModelInfo(id="mock/m1", name="M1", provider="mock", local=False)]

        @staticmethod
        def create_client(model, settings):
            client = MagicMock()
            client.model = model
            return client

    return MockProvider


class TestRegistration:
    """Test provider registration."""

    def test_register_without_provider_id_raises(self, registry):
        """Missing provider_id must raise ValueError."""
        with pytest.raises(ValueError, match="must have 'provider_id'"):

            @registry.register
            class NoId:
                pass

    def test_register_adds_to_providers(self, registry, mock_provider):
        """Registration adds provider to internal dict."""
        registry.register(mock_provider)
        assert registry._providers.get(mock_provider.provider_id) is mock_provider

    def test_register_returns_class(self, registry, mock_provider):
        """Registration returns the same class for decorator use."""
        result = registry.register(mock_provider)
        assert result is mock_provider


class TestLazyLoading:
    """Test lazy loading behavior."""

    def test_not_loaded_on_init(self):
        """Registry should not load providers on initialization."""
        reg = ProviderRegistry()
        assert not reg._loaded

    def test_ensure_loaded_returns_early_when_loaded(self, registry):
        """_ensure_loaded returns immediately if already loaded."""
        registry._loaded = True

        registry._ensure_loaded()

        assert registry._loaded

    def test_ensure_loaded_returns_early_inside_lock(self, registry):
        """_ensure_loaded returns inside lock when loaded flag flips."""
        registry._loaded = False

        class DummyLock:
            def __enter__(self):
                registry._loaded = True
                return self

            def __exit__(self, *args):
                return None

        registry._lock = DummyLock()

        registry._ensure_loaded()

        assert registry._loaded

    def test_loaded_after_get_models(self, registry, mock_provider):
        """get_available_models triggers lazy load."""
        registry.register(mock_provider)
        registry._loaded = False

        settings = MagicMock(api_key="key")
        registry.get_available_models(settings)

        assert registry._loaded

    def test_loaded_after_create_client(self, registry, mock_provider):
        """create_client triggers lazy load."""
        registry.register(mock_provider)
        registry._loaded = False

        settings = MagicMock(api_key="key")
        registry.create_client("mock/m1", settings)

        assert registry._loaded

    def test_ensure_loaded_is_idempotent(self, registry, mock_provider):
        """_ensure_loaded only loads once."""
        registry.register(mock_provider)

        # First load
        registry._ensure_loaded()
        assert registry._loaded

    def test_ensure_loaded_handles_import_errors(self, registry, monkeypatch):
        """_ensure_loaded handles ImportError and other exceptions."""
        original_import = __import__

        def fake_import(name, *args, **kwargs):
            if name == "src.infrastructure.adapters.llm.providers.anthropic":
                raise ImportError("missing")
            if name == "src.infrastructure.adapters.llm.providers.openai":
                raise Exception("boom")
            if name == "src.infrastructure.adapters.llm.providers.ollama":
                return MagicMock()
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", fake_import)

        registry._loaded = False
        registry._ensure_loaded()

        assert registry._loaded

        # Second load should be idempotent
        registry._ensure_loaded()
        assert registry._loaded


class TestGetAvailableModels:
    """Test getting available models."""

    def test_filters_unavailable_providers(self, registry):
        """Only available providers return models."""

        @registry.register
        class Unavailable:
            provider_id = "unavail"

            @staticmethod
            def is_available(settings):
                return False

            @staticmethod
            def list_models():
                return [
                    ModelInfo(id="unavail/m", name="M", provider="unavail", local=False)
                ]

        settings = MagicMock()
        models = registry.get_available_models(settings)

        assert len(models) == 0

    def test_aggregates_multiple_providers(self, registry, mock_provider):
        """Returns models from all available providers."""
        registry.register(mock_provider)

        @registry.register
        class Other:
            provider_id = "other"

            @staticmethod
            def is_available(settings):
                return True

            @staticmethod
            def list_models():
                return [
                    ModelInfo(id="other/m", name="M", provider="other", local=False)
                ]

        settings = MagicMock(api_key="key")
        models = registry.get_available_models(settings)

        assert len(models) == 2
        ids = [m.id for m in models]
        assert "mock/m1" in ids and "other/m" in ids


class TestCreateClient:
    """Test creating clients."""

    def test_invalid_format_raises(self, registry):
        """Model ID without slash raises ValueError."""
        with pytest.raises(ValueError, match="Invalid model ID format"):
            registry.create_client("no-slash", MagicMock())

    @pytest.mark.parametrize("model_id", ["/model", "provider/", "provider//model"])
    def test_invalid_segment_raises(self, registry, model_id):
        """Model IDs with empty segments raise ValueError."""
        with pytest.raises(ValueError, match="Invalid model ID format"):
            registry.create_client(model_id, MagicMock())

    def test_unknown_provider_raises(self, registry):
        """Unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            registry.create_client("unknown/model", MagicMock())

    def test_unavailable_provider_raises(self, registry, mock_provider):
        """Unavailable provider raises ValueError."""
        registry.register(mock_provider)
        settings = MagicMock(api_key=None)

        with pytest.raises(ValueError, match="not configured"):
            registry.create_client("mock/m1", settings)

    def test_creates_client_with_model_name(self, registry, mock_provider):
        """Client receives model name without provider prefix."""
        registry.register(mock_provider)
        settings = MagicMock(api_key="key")

        client = registry.create_client("mock/complex/name", settings)

        assert client.model == "complex/name"

    def test_creates_client_for_available_provider(self, registry, mock_provider):
        """Successfully creates client when provider is available."""
        registry.register(mock_provider)
        settings = MagicMock(api_key="key")

        client = registry.create_client("mock/m1", settings)

        assert client is not None
        assert client.model == "m1"


class TestIsProviderRegistered:
    """Test is_provider_registered method."""

    def test_returns_true_for_registered_provider(self, registry, mock_provider):
        """Returns True when provider is registered."""
        registry.register(mock_provider)

        assert registry.is_provider_registered("mock")

    def test_returns_false_for_unregistered_provider(self, registry):
        """Returns False when provider is not registered."""
        assert not registry.is_provider_registered("unknown")

    def test_triggers_lazy_load(self, registry):
        """is_provider_registered triggers lazy loading."""
        registry._loaded = False

        registry.is_provider_registered("unknown")

        assert registry._loaded


class TestGetRegisteredProviders:
    """Test get_registered_providers method."""

    def test_returns_registered_provider_ids(self, registry, mock_provider):
        registry.register(mock_provider)

        providers = registry.get_registered_providers()

        assert "mock" in providers


class TestClear:
    """Test clear method."""

    def test_clears_providers_and_loaded_flag(self, registry, mock_provider):
        """Clear resets providers and loaded state."""
        registry.register(mock_provider)
        registry._ensure_loaded()

        registry.clear()

        assert len(registry._providers) == 0
        assert not registry._loaded


class TestGlobalRegistry:
    """Tests for global registry and decorator."""

    def test_register_provider_decorator_uses_global_registry(self) -> None:
        """register_provider should register classes on global registry."""
        original_providers = dict(global_registry._providers)
        original_loaded = global_registry._loaded

        try:
            global_registry.clear()

            @register_provider
            class TempProvider:
                provider_id = "temp"
                provider_name = "Temp"

                @staticmethod
                def is_available(settings):
                    return True

                @staticmethod
                def list_models():
                    return []

                @staticmethod
                def create_client(model, settings):
                    client = MagicMock()
                    client.model = model
                    return client

            assert global_registry.is_provider_registered("temp")

            client = global_registry.create_client("temp/model", MagicMock())
            assert client.model == "model"
        finally:
            global_registry._providers = original_providers
            global_registry._loaded = original_loaded
