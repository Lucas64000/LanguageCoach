"""
LLM Providers - Auto-discovered provider modules.

Each provider module (*.py) in this package is automatically discovered
and imported by the registry. Providers register themselves using the
@register_provider decorator.

To add a new provider:
1. Create a new file (e.g., gemini.py) in this directory
2. Implement a class with @register_provider decorator
3. It will be auto-discovered at startup
"""
