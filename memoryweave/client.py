"""MemoryWeave client — main entry point for the SDK.

This is what users import and interact with directly:

    >>> from memoryweave import MemoryWeave
    >>> memory = MemoryWeave()
    >>> memory.add("Ravi prefers dark mode and Python.")
    >>> ctx = memory.get("What does the user prefer?")

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig

# TODO [Ravi Kashyap] 2026-03-23 - These imports are stubs.
# Each will be implemented in its respective phase:
#   extractor  → Phase 2, Chapter 2.1 & 2.2
#   embedder   → Phase 3, Chapter 3.1
#   store      → Phase 3, Chapter 3.2
#   graph      → Phase 3, Chapter 3.3
#   ranker     → Phase 4, Chapter 4.2
# from memoryweave.extractor import Extractor
# from memoryweave.embedder import Embedder
# from memoryweave.store import BaseStore
# from memoryweave.graph import KnowledgeGraph
# from memoryweave.ranker import Ranker


class MemoryWeave:
    """Main MemoryWeave client.

    Orchestrates the full memory pipeline:
    text input → NLP extraction → embedding → storage → retrieval → context.

    Args:
        config: Optional MemoryConfig instance. Defaults to MemoryConfig()
            with sensible defaults (in-memory store, no API key needed).

    Example:
        >>> memory = MemoryWeave()
        >>> memory.add("I work as a Python developer.")
        >>> ctx = memory.get("What is the user's job?")
        >>> print(ctx.summary)

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        """Initialise the MemoryWeave client.

        Args:
            config: Configuration object. Uses defaults if not provided.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # [Ravi Kashyap] 2026-03-23 - Use defaults if no config is passed.
        self.config = config or MemoryConfig()

        # TODO [Ravi Kashyap] 2026-03-23 - Initialise sub-components here.
        # Will be wired up as each phase completes:
        #   self._extractor = Extractor(self.config)    # Phase 2
        #   self._embedder  = Embedder(self.config)     # Phase 3
        #   self._store     = BaseStore.create(config)  # Phase 3
        #   self._graph     = KnowledgeGraph(config)    # Phase 3
        #   self._ranker    = Ranker(config)            # Phase 4

    def add(self, text: str, session_id: str | None = None) -> None:
        """Add a memory from raw text.

        Runs the full pipeline: NLP extraction → embedding
        → vector store → knowledge graph update.

        Args:
            text: Raw text to extract memory from (a message, document,
                or any natural language input).
            session_id: Optional session namespace for multi-user
                isolation. Defaults to config.default_session_id.

        Raises:
            ExtractionError: If the NLP pipeline fails to process text.
            StoreError: If writing to the vector store fails.
            GraphError: If the knowledge graph update fails.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # [Ravi Kashyap] 2026-03-23 - Stub. Full implementation in Phase 4.
        _session = session_id or self.config.default_session_id
        raise NotImplementedError(
            "memory.add() will be implemented in Phase 4, Chapter 4.1. "
            f"session_id={_session!r}, text_length={len(text)}"
        )

    def get(self, query: str, session_id: str | None = None) -> object:
        """Retrieve relevant memories for a given query.

        Searches both the vector store and knowledge graph, fuses the
        results, and returns a ranked MemoryContext object.

        Args:
            query: Natural language query to search memories for.
            session_id: Optional session namespace. Defaults to
                config.default_session_id.

        Returns:
            MemoryContext: Structured result containing summary, facts,
                entities, and raw memory items.

        Raises:
            StoreError: If the vector store query fails.
            GraphError: If the knowledge graph query fails.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # [Ravi Kashyap] 2026-03-23 - Stub. Full implementation in Phase 4.
        _session = session_id or self.config.default_session_id
        raise NotImplementedError(
            "memory.get() will be implemented in Phase 4, Chapter 4.2. "
            f"session_id={_session!r}, query={query!r}"
        )

    def forget(self, session_id: str | None = None) -> None:
        """Delete all memories for a given session.

        Args:
            session_id: Session to clear. Defaults to
                config.default_session_id.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 6, Chapter 6.2.
        raise NotImplementedError(
            "memory.forget() will be implemented in Phase 6, Chapter 6.2."
        )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        return (
            f"MemoryWeave(store={self.config.store_type!r}, "
            f"top_k={self.config.top_k})"
        )
