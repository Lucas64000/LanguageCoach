"""
Unified Provider Registry for dynamic LLM provider management.

Singleton registry with lazy loading for fast imports and tests.
Provides clients for any use case (chat, feedback, summary).
Auto-discovers providers from the providers/ package.
"""

from __future__ import annotations

import importlib
import pkgutil
import threading
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

import structlog

from src.infrastructure.adapters.llm.models import (
    ModelCapability,
    ModelInfo,
    ProviderProtocol,
)

if TYPE_CHECKING:
    from src.infrastructure.adapters.llm.clients.base import BaseLLMClient
    from src.infrastructure.config.settings import Settings


T = TypeVar("T", bound=type)

logger = structlog.get_logger(__name__)

# Package path for auto-discovery
_PROVIDERS_PACKAGE = "src.infrastructure.adapters.llm.providers"


class ProviderRegistry:
    """
    Unified singleton registry for LLM providers.

    Providers are loaded lazily on first use for fast imports.
    Thread-safe implementation for concurrent access.

    This registry manages ALL LLM providers and can create clients
    for any use case (ConversationPartner, FeedbackProvider, SummaryProvider).
    """

    def __init__(self) -> None:
        """Initialize with empty provider dict and thread lock."""
        self._providers: dict[str, type[ProviderProtocol]] = {}
        self._loaded = False
        self._lock = threading.Lock()

    def _ensure_loaded(self) -> None:
        """
        Lazy load all providers on first use via auto-discovery.

        Auto-discovers and imports all modules in the providers/ package.
        Each module's @register_provider decorator triggers registration.
        Safe to call multiple times (idempotent).
        Thread-safe with double-check locking pattern.
        """
        if self._loaded:
            return

        with self._lock:
            # Double-check pattern for thread safety
            if self._loaded:
                return

            logger.debug("loading_providers")
            errors: list[str] = []

            # Auto-discover and import all provider modules
            try:
                providers_module = importlib.import_module(_PROVIDERS_PACKAGE)
                providers_path = Path(providers_module.__file__).parent

                for module_info in pkgutil.iter_modules([str(providers_path)]):
                    module_name = module_info.name
                    # Skip __init__ and private modules
                    if module_name.startswith("_"):
                        continue

                    try:
                        importlib.import_module(f"{_PROVIDERS_PACKAGE}.{module_name}")
                        logger.debug("provider_module_loaded", module=module_name)
                    except ImportError as e:
                        logger.debug(
                            "provider_not_available",
                            module=module_name,
                            reason=str(e),
                        )
                    except Exception as e:
                        error_msg = f"{module_name}: {e}"
                        errors.append(error_msg)
                        logger.error(
                            "provider_load_error", module=module_name, error=str(e)
                        )

            except ImportError as e:
                logger.error("providers_package_not_found", error=str(e))

            if errors:
                logger.warning("providers_load_errors", errors=errors)

            self._loaded = True
            logger.info(
                "providers_loaded",
                count=len(self._providers),
                providers=list(self._providers.keys()),
            )

    def register(self, provider_class: T) -> T:
        """
        Register a provider class.

        Called automatically by @register_provider decorator.

        Args:
            provider_class: Class implementing ProviderProtocol.

        Returns:
            The same class (allows decorator usage).

        Raises:
            ValueError: If provider_id attribute is missing.
        """
        provider_id = getattr(provider_class, "provider_id", None)
        if not provider_id:
            raise ValueError(
                f"{provider_class.__name__} must have 'provider_id' class attribute"
            )

        logger.debug(
            "registering_provider",
            provider_id=provider_id,
            class_name=provider_class.__name__,
        )
        self._providers[provider_id] = provider_class
        return provider_class

    def get_available_models(
        self,
        settings: Settings,
        capability: ModelCapability | None = None,
    ) -> list[ModelInfo]:
        """
        Get all models from providers that are configured.

        Filters out providers without API keys configured.
        Optionally filters by capability.

        Args:
            settings: Application settings with API keys.
            capability: Optional capability to filter models by.

        Returns:
            List of ModelInfo from all available providers.
        """
        self._ensure_loaded()

        models: list[ModelInfo] = []
        for provider_id, provider_class in self._providers.items():
            if provider_class.is_available(settings):
                provider_models = provider_class.list_models()

                # Filter by capability if specified
                if capability:
                    provider_models = [
                        m for m in provider_models if m.supports(capability)
                    ]

                models.extend(provider_models)
                logger.debug(
                    "provider_models_added",
                    provider=provider_id,
                    count=len(provider_models),
                )
            else:
                logger.debug("provider_not_configured", provider=provider_id)

        logger.info("available_models_fetched", total=len(models))
        return models

    def create_client(self, model_id: str, settings: Settings) -> BaseLLMClient:
        """
        Create an LLM client for a model.

        This is the unified method to get a client for any use case.

        Args:
            model_id: Format "provider/model-name" (e.g., "openai/gpt-4o").
            settings: Application settings for API keys.

        Returns:
            BaseLLMClient instance for the model.

        Raises:
            ValueError: If model ID format invalid or provider unavailable.
        """
        self._ensure_loaded()

        # Validate and parse model_id
        parts = model_id.split("/", 1)
        if len(parts) != 2 or not parts[0] or not parts[1] or parts[1].startswith("/"):
            raise ValueError(
                f"Invalid model ID format: '{model_id}'. Expected 'provider/model-name'"
            )

        provider_id, model_name = parts

        if provider_id not in self._providers:
            available = ", ".join(self._providers.keys())
            raise ValueError(
                f"Unknown provider: '{provider_id}'. Available providers: {available}"
            )

        provider_class = self._providers[provider_id]

        if not provider_class.is_available(settings):
            raise ValueError(
                f"Provider '{provider_id}' is not configured. "
                f"Check API key in settings."
            )

        logger.info("creating_llm_client", model_id=model_id, provider=provider_id)
        return provider_class.create_client(model_name, settings)

    def is_provider_registered(self, provider_id: str) -> bool:
        """
        Check if a provider is registered.

        Triggers lazy loading to ensure all providers are checked.

        Args:
            provider_id: Provider identifier (e.g., "openai").

        Returns:
            True if provider is registered.
        """
        self._ensure_loaded()
        return provider_id in self._providers

    def get_registered_providers(self) -> list[str]:
        """
        Get list of all registered provider IDs.

        Returns:
            List of provider identifiers.
        """
        self._ensure_loaded()
        return list(self._providers.keys())

    def clear(self) -> None:
        """
        Clear all registered providers.

        Used for testing to reset registry state.
        Also resets the loaded flag.
        """
        logger.debug("clearing_registry")
        self._providers.clear()
        self._loaded = False


# Global singleton instance
registry = ProviderRegistry()


def register_provider[T: type](cls: T) -> T:
    """
    Decorator to register a provider class.

    Usage:
        @register_provider
        class OpenAIProvider:
            provider_id = "openai"
            provider_name = "OpenAI"

            @staticmethod
            def is_available(settings: Settings) -> bool:
                return bool(settings.openai_api_key)

            @staticmethod
            def list_models() -> list[ModelInfo]:
                return [ModelInfo(...)]

            @staticmethod
            def create_client(model: str, settings: Settings) -> BaseLLMClient:
                return OpenAIClient(api_key=settings.openai_api_key, model=model)

    Args:
        cls: Provider class with required attributes and methods.

    Returns:
        The same class (transparent decorator).
    """
    return registry.register(cls)
