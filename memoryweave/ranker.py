"""Context ranker — fuses vector and graph results into a MemoryContext.

Takes raw results from both the vector store and knowledge graph,
applies score fusion weights, and returns a clean MemoryContext object
ready for injection into an LLM prompt.

Full implementation: Phase 4, Chapter 4.2.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig
from memoryweave.store import MemoryItem


class MemoryContext:
    """The structured response object returned by memory.get().

    This is what gets injected into your LLM prompt.

    Attributes:
        summary: 2-3 sentence natural language summary of relevant memories.
        facts: List of atomic fact strings extracted from memories.
        entities: Dict of entity type → list of entity names found.
        items: Raw list of MemoryItem objects for advanced usage.
        scores: Relevance scores for each item (0.0-1.0).

    Example:
        >>> ctx = memory.get("What does the user prefer?")
        >>> print(ctx.summary)
        "Ravi is a Python developer who prefers dark mode."
        >>> print(ctx.facts)
        ["Ravi prefers Python", "Ravi uses dark mode"]

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(
        self,
        summary: str = "",
        facts: list[str] | None = None,
        entities: dict[str, list[str]] | None = None,
        items: list[MemoryItem] | None = None,
        scores: list[float] | None = None,
    ) -> None:
        """Initialise a MemoryContext.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.summary = summary
        self.facts = facts or []
        self.entities = entities or {}
        self.items = items or []
        self.scores = scores or []

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        return (
            f"MemoryContext(facts={len(self.facts)}, "
            f"entities={len(self.entities)}, "
            f"items={len(self.items)})"
        )

    def to_prompt_string(self) -> str:
        """Format the context as a string for LLM prompt injection.

        Returns:
            Formatted string combining summary and key facts,
            ready to insert into a system prompt.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 4, Chapter 4.2.
        raise NotImplementedError(
            "to_prompt_string() will be implemented in Phase 4, Chapter 4.2."
        )


class Ranker:
    """Fuses vector search and knowledge graph results into MemoryContext.

    Applies configurable weights to each score source and selects
    the top-k most relevant memories.

    Full implementation: Phase 4, Chapter 4.2.

    Args:
        config: MemoryConfig with vector_weight and graph_weight values.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(self, config: MemoryConfig) -> None:
        """Initialise the Ranker.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.config = config

    def fuse(
        self,
        vector_results: list[tuple[MemoryItem, float]],
        graph_results: list[tuple[str, float]],
    ) -> MemoryContext:
        """Fuse vector and graph results into a ranked MemoryContext.

        Args:
            vector_results: List of (MemoryItem, score) from vector store.
            graph_results: List of (fact_text, score) from knowledge graph.

        Returns:
            MemoryContext with fused, ranked results.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 4, Chapter 4.2.
        # Fusion formula: final_score = (vector_score * vector_weight)
        #                              + (graph_score  * graph_weight)
        # See docs/context-ranker.md for full benchmarks and decision log.
        raise NotImplementedError(
            "fuse() will be implemented in Phase 4, Chapter 4.2."
        )
