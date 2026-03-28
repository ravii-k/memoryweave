"""Main MemoryWeave client — this is what users actually interact with.

Tried to keep the public API as minimal as possible. Three methods:
add(), get(), forget(). That's it. Everything else is internal.

The client itself is just an orchestrator — it doesn't do any heavy
lifting, it just wires up the pipeline and delegates to the right
sub-components.
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig

# these will be uncommented one by one as each phase completes.
# leaving them here as a reminder of what needs to be wired up
# from memoryweave.extractor import Extractor   # Phase 2
# from memoryweave.embedder import Embedder     # Phase 3
# from memoryweave.store import BaseStore       # Phase 3
# from memoryweave.graph import KnowledgeGraph  # Phase 3
# from memoryweave.ranker import Ranker         # Phase 4


class MemoryWeave:
    """The main client. Start here.

    Orchestrates the full memory pipeline:
    text → NLP extraction → embedding → storage → retrieval → context.

    Args:
        config: Optional MemoryConfig. Defaults work fine for most cases —
            in-memory store, no API key, no external services needed.

    Example:
        >>> memory = MemoryWeave()
        >>> memory.add("I work as a Python developer in Bangalore.")
        >>> ctx = memory.get("Where does the user work?")
        >>> print(ctx.summary)
    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        """Set up the client with the given config or sensible defaults."""
        # if no config is passed just use defaults — zero friction for new users
        self.config = config or MemoryConfig()

        # sub-components get initialised here once each phase is done.
        # keeping these as comments so the structure is obvious when
        # we come back to wire things up
        # self._extractor = Extractor(self.config)    # Phase 2
        # self._embedder  = Embedder(self.config)     # Phase 3
        # self._store     = BaseStore.create(config)  # Phase 3
        # self._graph     = KnowledgeGraph(config)    # Phase 3
        # self._ranker    = Ranker(config)            # Phase 4

    def add(self, text: str, session_id: str | None = None) -> None:
        """Add a memory from raw text.

        Runs the full pipeline: NLP extraction → embedding
        → vector store → knowledge graph update.

        Args:
            text: Raw text to extract memory from. Can be a chat message,
                a document, or any natural language input.
            session_id: Optional namespace for isolating memories per user.
                Leave empty for single-user apps.

        Raises:
            ExtractionError: If NLP processing fails.
            StoreError: If writing to the vector store fails.
            GraphError: If the knowledge graph update fails.
        """
        # full pipeline gets wired in Phase 4, Chapter 4.1
        _session = session_id or self.config.default_session_id
        raise NotImplementedError(
            f"coming in Phase 4 — session={_session!r}, text_length={len(text)}"
        )

    def get(self, query: str, session_id: str | None = None) -> object:
        """Retrieve relevant memories for a query.

        Searches vector store + knowledge graph, fuses the scores,
        and returns the top results as a clean MemoryContext object.

        Args:
            query: Natural language question or prompt fragment.
            session_id: Optional namespace. Matches what was used in add().

        Returns:
            MemoryContext with summary, facts, entities, and raw items.

        Raises:
            StoreError: If the vector search fails.
            GraphError: If the graph query fails.
        """
        # full implementation in Phase 4, Chapter 4.2
        _session = session_id or self.config.default_session_id
        raise NotImplementedError(
            f"coming in Phase 4 — session={_session!r}, query={query!r}"
        )

    def forget(self, session_id: str | None = None) -> None:
        """Wipe all memories for a session.

        Args:
            session_id: Session to clear. Defaults to default_session_id.
        """
        # multi-user session management comes in Phase 6, Chapter 6.2
        raise NotImplementedError("coming in Phase 6")

    def __repr__(self) -> str:
        return (
            f"MemoryWeave(store={self.config.store_type!r}, top_k={self.config.top_k})"
        )
