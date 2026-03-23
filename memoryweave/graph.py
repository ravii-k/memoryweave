"""Knowledge graph — stores entities and relationships from extracted facts.

This sits alongside the vector store and handles the structured side of
memory retrieval. Vector search is great for semantic similarity but
terrible at answering questions like "what does Ravi prefer?" where you
need to traverse explicit entity relationships.

Using NetworkX for now because it's pure Python, zero infrastructure,
and good enough for single-user use cases. If we ever need to scale
to thousands of users with huge graphs, Neo4j would be the move —
but that's a future problem.

Each session gets its own isolated graph so user memories never bleed
into each other.
"""

from __future__ import annotations

# will be uncommented in Phase 3, Chapter 3.3
# import networkx as nx

from memoryweave.config import MemoryConfig
from memoryweave.extractor import EntityResult, FactResult


class KnowledgeGraph:
    """Builds and queries a graph of entities and relationships.

    Entities become nodes. Facts (SPO triples) become directed edges
    between nodes. Querying traverses the graph to find relevant facts
    for a given natural language query.

    Each session_id gets its own DiGraph so memories are fully isolated
    between users. The graphs live in memory for now — persistence via
    JSON serialisation comes later in Phase 3.

    Args:
        config: MemoryConfig instance. Not heavily used here yet but
            will matter when we add graph size limits in Phase 6.
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        # dict of session_id -> DiGraph so each user has their own graph.
        # initialised lazily — graph only created when first add() happens
        # self._graphs: dict[str, nx.DiGraph] = {}

    def add_entities(
        self, entities: list[EntityResult], session_id: str
    ) -> None:
        """Add extracted entities as nodes in the session graph.

        If an entity node already exists we update it rather than
        duplicating — deduplication is handled by entity text + label.

        Args:
            entities: Entities to add, straight from the Extractor.
            session_id: Which session's graph to update.
        """
        # Phase 3, Chapter 3.3
        raise NotImplementedError("coming in Phase 3, Chapter 3.3")

    def add_facts(
        self, facts: list[FactResult], session_id: str
    ) -> None:
        """Add extracted facts as directed edges between entity nodes.

        Subject and object become nodes if they don't exist yet.
        The predicate becomes the edge label.

        Args:
            facts: SPO triples to add, straight from the Extractor.
            session_id: Which session's graph to update.
        """
        # Phase 3, Chapter 3.3
        raise NotImplementedError("coming in Phase 3, Chapter 3.3")

    def query(
        self, query: str, session_id: str, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Find relevant facts in the graph for a given query.

        Converts the query to entity mentions, finds matching nodes,
        and returns neighbouring facts ranked by relevance.

        Args:
            query: Natural language query string.
            session_id: Which session's graph to search.
            top_k: Max number of facts to return.

        Returns:
            List of (fact_text, relevance_score) tuples, best first.
        """
        # Phase 3, Chapter 3.3 — the scoring logic here will be
        # simple at first (node degree + string match) and can be
        # improved later if needed
        raise NotImplementedError("coming in Phase 3, Chapter 3.3")
