"""LLM adapter package for MemoryWeave.

Adapters handle automatic context injection into LLM API calls.
Each adapter wraps a specific LLM SDK and injects MemoryContext
into the messages before sending.

Available adapters (implemented in Phase 4, Chapter 4.3):
- OpenAIAdapter    — for OpenAI GPT models
- AnthropicAdapter — for Anthropic Claude models
- OllamaAdapter    — for local models via Ollama

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

# TODO [Ravi Kashyap] 2026-03-23 - Export adapters here once implemented.
# Phase 4, Chapter 4.3:
# from memoryweave.adapters.openai import OpenAIAdapter      # noqa: F401
# from memoryweave.adapters.anthropic import AnthropicAdapter # noqa: F401
# from memoryweave.adapters.ollama import OllamaAdapter      # noqa: F401

__all__: list[str] = []
