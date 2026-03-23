"""Knowledge graph — entity and relationship storage using NetworkX.

Stores entities as nodes and relationships as edges. Provides graph
traversal queries to complement vector search during retrieval.

Full implementation: Phase 3, Chapter 3.3.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

# TODO [Ravi Kashyap] 2026-03-23 - Uncomment in Phase 3, Chapter 3.3.
# import networkx as nx

from memoryweave.config import MemoryConfig
from memoryweave.extractor import EntityResult, FactResult


class KnowledgeGraph:
    """Entity and relationship graph built from extracted facts.

    Each session has its own isolated graph. Nodes are entities
    (people, places, organisations, concepts). Edges are the
    relationships between them (extracted as FactResult triples).

    Full implementation: Phase 3, Chapter 3.3.

    Args:
        config: MemoryConfig instance.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(self, config: MemoryConfig) -> None:
        """Initialise the KnowledgeGraph.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.config = config
        # TODO [Ravi Kashyap] 2026-03-23 - Init NetworkX graph in Phase 3.
        # self._graphs: dict[str, nx.DiGraph] = {}

    def add_entities(
        self, entities: list[EntityResult], session_id: str
    ) -> None:
        """Add extracted entities as nodes to the session graph.

        Args:
            entities: List of EntityResult objects to add.
            session_id: Session namespace for the graph.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 3, Chapter 3.3.
        raise NotImplementedError(
            "add_entities() will be implemented in Phase 3, Chapter 3.3."
        )

    def add_facts(
        self, facts: list[FactResult], session_id: str
    ) -> None:
        """Add extracted facts as edges between entity nodes.

        Args:
            facts: List of FactResult triples to add as edges.
            session_id: Session namespace for the graph.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 3, Chapter 3.3.
        raise NotImplementedError(
            "add_facts() will be implemented in Phase 3, Chapter 3.3."
        )

    def query(
        self, query: str, session_id: str, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Query the knowledge graph for relevant facts.

        Args:
            query: Natural language query string.
            session_id: Session namespace to search within.
            top_k: Maximum number of results to return.

        Returns:
            List of (fact_text, relevance_score) tuples.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 3, Chapter 3.3.
        raise NotImplementedError(
            "query() will be implemented in Phase 3, Chapter 3.3."
        )
