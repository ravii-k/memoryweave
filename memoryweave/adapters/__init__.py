"""LLM adapters — automatic context injection for each supported LLM SDK.

Each adapter wraps a specific LLM SDK and handles injecting MemoryContext
into the messages automatically. Without an adapter users have to do the
injection manually — which works fine but adapters make it seamless.

Keeping this empty for now. All three adapters get built in Phase 4,
Chapter 4.3. Uncommenting the imports below is how they get exposed.
"""

# Phase 4, Chapter 4.3:
# from memoryweave.adapters.openai import OpenAIAdapter        # noqa: F401
# from memoryweave.adapters.anthropic import AnthropicAdapter  # noqa: F401
# from memoryweave.adapters.ollama import OllamaAdapter        # noqa: F401

__all__: list[str] = []
