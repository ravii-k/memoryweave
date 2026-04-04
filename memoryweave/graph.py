"""Knowledge graph — stores entities as nodes and facts as edges.

Uses NetworkX DiGraph under the hood. Each session gets its own
isolated graph so memories never bleed between users.

The graph complements the vector store — vector search is great for
semantic similarity, the graph is great for structured entity queries
like "what does Ravi prefer?" or "where does Ravi work?".

Phase 3, Chapter 3.3 — Ravi Kashyap 2026-04-03
"""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from memoryweave.config import MemoryConfig
from memoryweave.errors import GraphError
from memoryweave.extractor import EntityResult, FactResult
from memoryweave.logger import get_logger

logger = get_logger(__name__)


class KnowledgeGraph:
    """Entity and relationship graph built from extracted facts.

    Each session has its own isolated DiGraph. Nodes are entities
    (people, places, orgs, concepts). Edges are relationships
    extracted as FactResult triples.

    Args:
    ----
        config: MemoryConfig instance.

    Example:
    -------
        >>> kg = KnowledgeGraph(MemoryConfig())
        >>> entities = [EntityResult("Ravi", "PERSON")]
        >>> kg.add_entities(entities, session_id="default")
        >>> results = kg.query("Ravi", session_id="default")

    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        # lazy-init per session — graph only created when first add() happens
        self._graphs: dict[str, nx.DiGraph] = {}

    def _get_graph(self, session_id: str) -> nx.DiGraph:
        """Get or create the DiGraph for a session."""
        if session_id not in self._graphs:
            self._graphs[session_id] = nx.DiGraph()
            logger.debug("created new graph for session %r", session_id)
        return self._graphs[session_id]

    def add_entities(self, entities: list[EntityResult], session_id: str) -> None:
        """Add extracted entities as nodes in the session graph.

        If an entity node already exists we update its label attribute
        rather than creating a duplicate — dedup by (text, label).

        Args:
        ----
            entities: EntityResult list straight from the Extractor.
            session_id: Which session's graph to update.

        Raises:
        ------
            GraphError: If the graph operation fails.

        """
        try:
            graph = self._get_graph(session_id)
            for entity in entities:
                node_id = f"{entity.label}:{entity.text}"
                if not graph.has_node(node_id):
                    graph.add_node(
                        node_id,
                        text=entity.text,
                        label=entity.label,
                        confidence=entity.confidence,
                    )
                    logger.debug("added node %r to session %r", node_id, session_id)
        except Exception as e:
            raise GraphError(f"add_entities failed: {e}") from e

    def add_facts(self, facts: list[FactResult], session_id: str) -> None:
        """Add extracted facts as directed edges between nodes.

        Subject and object become nodes if they don't exist yet.
        The predicate becomes the edge label.

        Args:
        ----
            facts: FactResult triples from the Extractor.
            session_id: Which session's graph to update.

        Raises:
        ------
            GraphError: If the graph operation fails.

        """
        try:
            graph = self._get_graph(session_id)
            for fact in facts:
                subj_id = f"FACT_NODE:{fact.subject}"
                obj_id = f"FACT_NODE:{fact.obj}"

                # add nodes if they don't exist
                if not graph.has_node(subj_id):
                    graph.add_node(subj_id, text=fact.subject, label="FACT_NODE")
                if not graph.has_node(obj_id):
                    graph.add_node(obj_id, text=fact.obj, label="FACT_NODE")

                # add the directed edge — subject -> object via predicate
                graph.add_edge(
                    subj_id,
                    obj_id,
                    predicate=fact.predicate,
                    confidence=fact.confidence,
                    temporal=fact.temporal,
                )
                logger.debug(
                    "added edge %r -[%s]-> %r in session %r",
                    fact.subject,
                    fact.predicate,
                    fact.obj,
                    session_id,
                )
        except Exception as e:
            raise GraphError(f"add_facts failed: {e}") from e

    def query(self, query: str, session_id: str, top_k: int = 5) -> list[tuple[str, float]]:
        """Find relevant facts in the graph for a given query string.

        Does a simple string-match search over node text and edge
        predicates. Returns (fact_text, relevance_score) tuples.

        Not doing semantic search here — that's the vector store's job.
        The graph is for structured lookups: "what does Ravi prefer?"
        finds edges where Ravi is the subject.

        Args:
        ----
            query: Natural language query string.
            session_id: Which session's graph to search.
            top_k: Maximum number of results to return.

        Returns:
        -------
            List of (fact_text, relevance_score) tuples, best first.

        Raises:
        ------
            GraphError: If the query fails.

        """
        try:
            graph = self._get_graph(session_id)
            if graph.number_of_nodes() == 0:
                return []

            query_lower = query.lower()
            results: list[tuple[str, float]] = []

            for subj, obj, data in graph.edges(data=True):
                subj_text = graph.nodes[subj].get("text", "")
                obj_text = graph.nodes[obj].get("text", "")
                predicate = data.get("predicate", "")
                confidence = data.get("confidence", 0.8)

                fact_text = f"{subj_text} {predicate} {obj_text}"

                # simple relevance: exact match > partial match
                score = 0.0
                if query_lower in fact_text.lower():
                    score = confidence
                elif any(
                    word in fact_text.lower() for word in query_lower.split() if len(word) > 2
                ):
                    score = confidence * 0.5

                if score > 0:
                    results.append((fact_text, score))

            # sort by score descending and return top_k
            results.sort(key=lambda x: x[1], reverse=True)
            top = results[:top_k]

            logger.debug(
                "graph query returned %d results for session %r",
                len(top),
                session_id,
            )
            return top

        except Exception as e:
            raise GraphError(f"query failed: {e}") from e

    def get_entity_facts(self, entity_text: str, session_id: str) -> list[tuple[str, float]]:
        """Get all facts about a specific entity.

        Finds all edges where this entity is the subject or object.

        Args:
        ----
            entity_text: The entity name to look up.
            session_id: Which session to search.

        Returns:
        -------
            List of (fact_text, score) tuples.

        """
        try:
            graph = self._get_graph(session_id)
            results: list[tuple[str, float]] = []

            for subj, obj, data in graph.edges(data=True):
                subj_text = graph.nodes[subj].get("text", "")
                obj_text = graph.nodes[obj].get("text", "")
                predicate = data.get("predicate", "")
                confidence = data.get("confidence", 0.8)

                if (
                    entity_text.lower() in subj_text.lower()
                    or entity_text.lower() in obj_text.lower()
                ):
                    fact = f"{subj_text} {predicate} {obj_text}"
                    results.append((fact, confidence))

            return results
        except Exception as e:
            raise GraphError(f"get_entity_facts failed: {e}") from e

    def node_count(self, session_id: str) -> int:
        """Return the number of nodes in the session graph."""
        return self._get_graph(session_id).number_of_nodes()

    def edge_count(self, session_id: str) -> int:
        """Return the number of edges in the session graph."""
        return self._get_graph(session_id).number_of_edges()

    def delete_session(self, session_id: str) -> None:
        """Wipe the entire graph for a session."""
        if session_id in self._graphs:
            del self._graphs[session_id]
            logger.debug("deleted graph for session %r", session_id)

    def save(self, session_id: str, path: str) -> None:
        """Persist the session graph to a JSON file.

        Args:
        ----
            session_id: Session to save.
            path: File path to write to.

        """
        try:
            graph = self._get_graph(session_id)
            data = nx.node_link_data(graph)
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug("saved graph for session %r to %r", session_id, path)
        except Exception as e:
            raise GraphError(f"save failed: {e}") from e

    def load(self, session_id: str, path: str) -> None:
        """Load a session graph from a JSON file.

        Args:
        ----
            session_id: Session ID to assign to the loaded graph.
            path: File path to read from.

        """
        try:
            with open(path) as f:
                data = json.load(f)
            self._graphs[session_id] = nx.node_link_graph(data)
            logger.debug("loaded graph for session %r from %r", session_id, path)
        except Exception as e:
            raise GraphError(f"load failed: {e}") from e
