"""Ranker — fuses vector search results with graph query results.

Takes raw results from the vector store and the knowledge graph,
scores them using a weighted fusion formula, and returns a
MemoryContext ready to inject into an LLM prompt.

Fusion formula:
    final_score = (vector_weight * vector_score) + (graph_weight * graph_score)

Default weights: 0.6 vector / 0.4 graph (set in MemoryConfig).

Phase 4, Chapter 4.1 — Ravi Kashyap 2026-04-03
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig
from memoryweave.logger import get_logger
from memoryweave.store import MemoryItem

logger = get_logger(__name__)


class MemoryContext:
    """The result of a memory.get() call — ready to inject into a prompt.

    Attributes
    ----------
        summary: Plain-text summary of relevant memories. Inject this
            directly into the LLM system prompt.
        facts: List of (fact_text, score) tuples from the knowledge graph.
        entries: List of (MemoryItem, score) tuples from the vector store.
        scores: Flat list of final fusion scores for each entry.

    """

    def __init__(
        self,
        summary: str = "",
        facts: list[tuple[str, float]] | None = None,
        entries: list[tuple[MemoryItem, float]] | None = None,
        scores: list[float] | None = None,
    ) -> None:
        self.summary = summary
        self.facts = facts or []
        self.entries = entries or []
        self.scores = scores or []

    def __repr__(self) -> str:
        return (
            f"MemoryContext(facts={len(self.facts)}, "
            f"entries={len(self.entries)}, "
            f"summary_len={len(self.summary)})"
        )

    @property
    def has_results(self) -> bool:
        """True if there is any memory context to inject."""
        return bool(self.entries or self.facts)


class Ranker:
    """Fuses vector store and graph results into a MemoryContext.

    Called at the end of every memory.get() to combine both retrieval
    signals into a single ranked list and build the context summary.

    Args:
    ----
        config: MemoryConfig with vector_weight and graph_weight set.

    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config

    def fuse(
        self,
        vector_results: list[tuple[MemoryItem, float]],
        graph_results: list[tuple[str, float]],
        top_k: int | None = None,
    ) -> MemoryContext:
        """Fuse vector and graph results into a MemoryContext.

        Args:
        ----
            vector_results: List of (MemoryItem, score) from BaseStore.search().
            graph_results: List of (fact_text, score) from KnowledgeGraph.query().
            top_k: Max entries to include. Defaults to config.top_k.

        Returns:
        -------
            A MemoryContext with summary, facts, entries, and scores.

        """
        k = top_k if top_k is not None else self.config.top_k
        vw = self.config.vector_weight
        gw = self.config.graph_weight

        logger.debug(
            "fusing %d vector + %d graph results (vw=%.1f, gw=%.1f)",
            len(vector_results),
            len(graph_results),
            vw,
            gw,
        )

        # normalise graph scores to 0-1 range if needed
        graph_max = max((s for _, s in graph_results), default=1.0)
        if graph_max == 0.0:
            graph_max = 1.0

        # build a text → graph_score lookup for fusion
        graph_lookup: dict[str, float] = {text: score / graph_max for text, score in graph_results}

        # score each vector result with fusion
        fused: list[tuple[MemoryItem, float]] = []
        for item, vscore in vector_results:
            # check if any graph fact mentions text from this memory
            gscore = max(
                (
                    graph_lookup[gtext]
                    for gtext in graph_lookup
                    if any(
                        word in item.text.lower() for word in gtext.lower().split() if len(word) > 3
                    )
                ),
                default=0.0,
            )
            final = (vw * vscore) + (gw * gscore)
            fused.append((item, final))

        # sort by final score, take top_k
        fused.sort(key=lambda x: x[1], reverse=True)
        top_entries = fused[:k]
        top_scores = [score for _, score in top_entries]

        # also include graph-only facts that aren't in vector results
        top_facts = graph_results[:k]

        summary = self._build_summary(top_entries, top_facts)

        logger.debug(
            "fuse complete — %d entries, %d facts in context",
            len(top_entries),
            len(top_facts),
        )

        return MemoryContext(
            summary=summary,
            facts=top_facts,
            entries=top_entries,
            scores=top_scores,
        )

    def _build_summary(
        self,
        entries: list[tuple[MemoryItem, float]],
        facts: list[tuple[str, float]],
    ) -> str:
        """Build the plain-text summary to inject into the LLM prompt.

        Keeps it concise — one sentence per memory, facts listed cleanly.
        The LLM will do the synthesis; we just provide the raw context.
        """
        if not entries and not facts:
            return ""

        lines: list[str] = []

        if entries:
            lines.append("Relevant memories:")
            for item, score in entries:
                lines.append(f"- {item.text} (relevance: {score:.2f})")

        if facts:
            lines.append("Known facts:")
            for fact_text, score in facts:
                lines.append(f"- {fact_text} (confidence: {score:.2f})")

        return "\n".join(lines)
