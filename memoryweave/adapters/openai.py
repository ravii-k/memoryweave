"""OpenAI adapter — injects MemoryWeave context into OpenAI chat calls."""

from __future__ import annotations

from typing import Any

from memoryweave.adapters.base import BaseAdapter
from memoryweave.client import MemoryWeave
from memoryweave.logger import get_logger

logger = get_logger(__name__)

_MEMORY_HEADER = "\n\n---\nWhat you remember about this user:\n"


class OpenAIAdapter(BaseAdapter):
    """Wraps MemoryWeave around OpenAI's chat completions API.

    Automatically retrieves relevant memories and injects them
    into the system prompt before every call.

    Example:
    -------
        >>> from openai import OpenAI
        >>> from memoryweave import MemoryWeave
        >>> from memoryweave.adapters.openai import OpenAIAdapter
        >>>
        >>> memory = MemoryWeave()
        >>> adapter = OpenAIAdapter(memory)
        >>> client = OpenAI()
        >>>
        >>> messages = [{"role": "user", "content": "What stack should I use?"}]
        >>> messages = adapter.prepare(messages)
        >>> response = client.chat.completions.create(
        ...     model="gpt-4o", messages=messages
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
        """Inject memory context into the system message."""
        result = list(messages)
        memory_block = _MEMORY_HEADER + context_summary

        # if a system message exists, append to it
        for i, msg in enumerate(result):
            if msg.get("role") == "system":
                result[i] = {
                    **msg,
                    "content": msg["content"] + memory_block,
                }
                return result

        # no system message — prepend one
        result.insert(
            0,
            {
                "role": "system",
                "content": self.system_prompt + memory_block,
            },
        )
        return result

    def prepare(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Retrieve memory and return messages ready to send to OpenAI.

        Args:
        ----
            messages: Your original messages list.

        Returns:
        -------
            Messages with memory context injected into system prompt.

        """
        # use the last user message as the query
        query = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                query = str(msg.get("content", ""))
                break

        if not query:
            logger.debug("OpenAIAdapter.prepare() — no user message found, skipping")
            return messages

        ctx = self.memory.get(query, top_k=self.top_k)
        if not ctx.has_results:
            logger.debug("OpenAIAdapter.prepare() — no memories found for query")
            return messages

        logger.debug("OpenAIAdapter.prepare() — injecting %d memories", len(ctx.entries))
        return self.inject(messages, ctx.summary)

    def remember(self, messages: list[dict[str, Any]]) -> None:
        """Store all user messages from a conversation into memory.

        Call this after a conversation turn to keep memory up to date.

        Args:
        ----
            messages: The messages list from the conversation.

        """
        for msg in messages:
            if msg.get("role") == "user":
                content = str(msg.get("content", "")).strip()
                if content:
                    self.memory.add(content)
