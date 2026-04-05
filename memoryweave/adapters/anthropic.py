"""Anthropic adapter — injects MemoryWeave context into Anthropic API calls."""

from __future__ import annotations

from typing import Any

from memoryweave.adapters.base import BaseAdapter
from memoryweave.client import MemoryWeave
from memoryweave.logger import get_logger

logger = get_logger(__name__)

_MEMORY_HEADER = "\n\n---\nWhat you remember about this user:\n"


class AnthropicAdapter(BaseAdapter):
    """Wraps MemoryWeave around Anthropic's Messages API.

    Automatically retrieves relevant memories and injects them
    into the system prompt before every call.

    Example:
    -------
        >>> import anthropic
        >>> from memoryweave import MemoryWeave
        >>> from memoryweave.adapters.anthropic import AnthropicAdapter
        >>>
        >>> memory = MemoryWeave()
        >>> adapter = AnthropicAdapter(memory)
        >>> client = anthropic.Anthropic()
        >>>
        >>> messages = [{"role": "user", "content": "What stack should I use?"}]
        >>> system, messages = adapter.prepare(messages)
        >>> response = client.messages.create(
        ...     model="claude-opus-4-6",
        ...     system=system,
        ...     messages=messages,
        ...     max_tokens=1024,
        ... )

    """

    def __init__(
        self,
        memory: MemoryWeave,
        system_prompt: str = "You are a helpful assistant.",
        top_k: int | None = None,
    ) -> None:
        self.memory = memory
        self.system_prompt = system_prompt
        self.top_k = top_k

    def inject(
        self,
        messages: list[dict[str, Any]],
        context_summary: str,
    ) -> list[dict[str, Any]]:
        """Anthropic keeps system separate — inject returns messages unchanged.

        System prompt is handled by prepare() which returns it separately.
        """
        return messages

    def prepare(
        self,
        messages: list[dict[str, Any]],
    ) -> tuple[str, list[dict[str, Any]]]:
        """Retrieve memory and return (system_prompt, messages) for Anthropic.

        Args:
        ----
            messages: Your original messages list (no system role).

        Returns:
        -------
            Tuple of (system_string, messages) ready for client.messages.create().

        """
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    query = content
                elif isinstance(content, list):
                    # handle content blocks format
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            query = block.get("text", "")
                            break
                break

        system = self.system_prompt

        if not query:
            logger.debug("AnthropicAdapter.prepare() — no user message found")
            return system, messages

        ctx = self.memory.get(query, top_k=self.top_k)
        if ctx.has_results:
            system += _MEMORY_HEADER + ctx.summary
            logger.debug("AnthropicAdapter.prepare() — injecting %d memories", len(ctx.entries))

        return system, messages

    def remember(self, messages: list[dict[str, Any]]) -> None:
        """Store all user messages from a conversation into memory.

        Args:
        ----
            messages: The messages list from the conversation.

        """
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    self.memory.add(content)
                elif isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text = block.get("text", "").strip()
                            if text:
                                self.memory.add(text)
