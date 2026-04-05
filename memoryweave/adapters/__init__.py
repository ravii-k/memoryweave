"""LLM adapters — automatic memory injection for OpenAI and Anthropic."""

from memoryweave.adapters.anthropic import AnthropicAdapter
from memoryweave.adapters.openai import OpenAIAdapter

__all__ = ["OpenAIAdapter", "AnthropicAdapter"]
