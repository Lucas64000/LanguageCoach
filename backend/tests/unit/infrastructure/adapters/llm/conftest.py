"""
Test configuration for LLM infrastructure tests.

Fixtures are kept local to each test file for clarity:
- test_services.py: Service-level fixtures (mock_client, sample_messages, etc.)
- test_openai_client.py: OpenAI client fixtures (mock_openai_async_client, etc.)
- test_registry.py: Registry fixtures (mock_provider, etc.)

Shared fixtures can be added here when multiple test files need them.
"""
