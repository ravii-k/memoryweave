"""Context ranker — fuses vector and graph results into a clean MemoryContext.

This is the last stage before results go back to the user. Takes raw
results from both the vector store and knowledge graph, applies score
fusion, and packages everything into a MemoryContext that's ready to
inject into an LLM prompt.

Score fusion is simple for now: weighted sum of vector score and graph
score. Started with equal weights but vector search was outperforming
graph on most queries so bumped it to 60/40. Will benchmark properly
in Phase 4 and adjust if needed.
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig
from memoryweave.store import MemoryItem


class MemoryContext:
    """What memory.get() returns — structured and ready for prompt injection.

    This is the object users interact with after calling get(). Designed
    to be easy to use — most users just want ctx.summary and that's it.
    The raw items and scores are there for power users who need more control.

    Attributes:
        summary: 2-3 sentence natural language summary of the most relevant
            memories. This is what you inject into your system prompt.
        facts: Individual atomic facts pulled from memories. More granular
            than the summary — useful for debugging what was retrieved.
        entities: Dict grouping entity names by type. e.g.
            {"PERSON": ["Ravi"], "ORG": ["Anthropic"]}
        items: The raw MemoryItem objects for anyone who needs the full data.
        scores: Relevance score for each item, same order as items.
            Scores are 0.0–1.0, higher is more relevant.

    Example:
        >>> ctx = memory.get("What does the user prefer?")
        >>> print(ctx.summary)
        "Ravi is a Python developer who prefers dark mode."
        >>> print(ctx.facts)
        ["Ravi prefers Python", "Ravi uses dark mode"]
    """

    def __init__(
        self,
        summary: str = "",
        facts: list[str] | None = None,
        entities: dict[str, list[str]] | None = None,
        items: list[MemoryItem] | None = None,
        scores: list[float] | None = None,
    ) -> None:
        self.summary = summary
        self.facts = facts or []
        self.entities = entities or {}
        self.items = items or []
        self.scores = scores or []

    def __repr__(self) -> str:
        return (
            f"MemoryContext(facts={len(self.facts)}, "
            f"entities={len(self.entities)}, "
            f"items={len(self.items)})"
        )

    def to_prompt_string(self) -> str:
        """Format the context as a string ready to drop into a system prompt.

        Returns:
            Formatted string combining summary and key facts. Keeps it
            concise — don't want to eat too many tokens with memory context.
        """
        # Phase 4, Chapter 4.2 — will experiment with different formats
        # to find what actually improves LLM response quality
        raise NotImplementedError("coming in Phase 4, Chapter 4.2")


class Ranker:
    """Fuses vector and graph scores into a ranked MemoryContext.

    The fusion formula is straightforward:
        final_score = (vector_score * vector_weight)
                    + (graph_score  * graph_weight)

    Then we sort by final_score descending and take top_k.

    Args:
        config: Provides vector_weight, graph_weight, and top_k.
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config

    def fuse(
        self,
        vector_results: list[tuple[MemoryItem, float]],
        graph_results: list[tuple[str, float]],
    ) -> MemoryContext:
        """Fuse vector and graph results into a ranked MemoryContext.

        Args:
            vector_results: (MemoryItem, score) pairs from the vector store.
            graph_results: (fact_text, score) pairs from the knowledge graph.

        Returns:
            MemoryContext with the best fused results, ready for injection.
        """
        # Phase 4, Chapter 4.2.
        # the tricky part here will be aligning vector and graph results
        # since they come in different formats — need to normalise scores
        # to the same scale before fusing
        raise NotImplementedError("coming in Phase 4, Chapter 4.2")
