"""Base adapter interface for LLM integrations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Base class for all LLM adapters.

    Adapters wrap a specific LLM SDK and handle injecting
    MemoryContext into messages automatically.
    """

    @abstractmethod
    def inject(
        self,
        messages: list[dict[str, Any]],
        context_summary: str,
    ) -> list[dict[str, Any]]:
        """Inject memory context into a messages list.

        Args:
        ----
            messages: The original messages list for the LLM.
            context_summary: Plain-text summary from MemoryContext.

        Returns:
        -------
            Updated messages list with memory injected into system prompt.

        """
