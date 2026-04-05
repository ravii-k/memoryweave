"""MemoryWeave client — the main public API.

Three lines of code to add persistent memory to any LLM app:

    memory = MemoryWeave()
    memory.add("My name is Ravi and I prefer Python.")
    ctx = memory.get("What language does the user prefer?")
    # inject ctx.summary into your LLM system prompt

Phase 4, Chapter 4.1 — Ravi Kashyap 2026-04-03
"""

from __future__ import annotations

from memoryweave.config import MemoryConfig
from memoryweave.embedder import Embedder
from memoryweave.errors import MemoryWeaveError
from memoryweave.extractor import Extractor
from memoryweave.graph import KnowledgeGraph
from memoryweave.logger import get_logger
from memoryweave.ranker import MemoryContext, Ranker
from memoryweave.store import BaseStore, MemoryItem

logger = get_logger(__name__)


class MemoryWeave:
    """Universal long-term memory for any LLM application.

    Automatically extracts entities and facts from text, stores
    embeddings for semantic search, and builds a knowledge graph
    for structured queries. Returns fused context ready to inject
    into any LLM prompt.

    Args:
    ----
        config: Optional MemoryConfig. Defaults to in-memory store
            with all-MiniLM-L6-v2 embeddings and spaCy NLP.

    Example:
    -------
        >>> memory = MemoryWeave()
        >>> memory.add("My name is Ravi and I prefer Python.")
        >>> ctx = memory.get("What language does the user prefer?")
        >>> print(ctx.summary)

    """

    def __init__(self, config: MemoryConfig | None = None) -> None:
        self.config = config or MemoryConfig()
        self._dedup_threshold: float = 0.98

        # lazy-init the heavy components — spaCy and sentence-transformers
        # both take ~1s to load, so we defer until first use
        self._extractor: Extractor | None = None
        self._embedder: Embedder | None = None
        self._store: BaseStore | None = None
        self._graph: KnowledgeGraph | None = None
        self._ranker: Ranker = Ranker(self.config)

        logger.debug(
            "MemoryWeave initialised (store=%r, model=%r)",
            self.config.store_type,
            self.config.embedding_model,
        )

    @property
    def extractor(self) -> Extractor:
        """Lazy-load the spaCy extractor on first use."""
        if self._extractor is None:
            logger.debug("loading extractor...")
            self._extractor = Extractor(self.config)
        return self._extractor

    @property
    def embedder(self) -> Embedder:
        """Lazy-load the sentence-transformers embedder on first use."""
        if self._embedder is None:
            logger.debug("loading embedder...")
            self._embedder = Embedder(self.config)
        return self._embedder

    @property
    def store(self) -> BaseStore:
        """Lazy-load the vector store on first use."""
        if self._store is None:
            logger.debug("initialising store (type=%r)...", self.config.store_type)
            self._store = BaseStore.create(self.config)
        return self._store

    @property
    def graph(self) -> KnowledgeGraph:
        """Lazy-load the knowledge graph on first use."""
        if self._graph is None:
            logger.debug("initialising knowledge graph...")
            self._graph = KnowledgeGraph(self.config)
        return self._graph

    def add(self, text: str, metadata: dict | None = None) -> MemoryItem:
        """Extract, embed, and store a memory from raw text.

        Runs the full pipeline:
        1. Extract entities and facts (spaCy)
        2. Embed the raw text (sentence-transformers)
        3. Store embedding in vector store
        4. Add entities and facts to knowledge graph

        Args:
        ----
            text: Raw text to remember. Can be a sentence, paragraph,
                or full conversation turn.
            metadata: Optional key-value metadata to attach to the memory.

        Returns:
        -------
            The MemoryItem that was stored.

        Raises:
        ------
            MemoryWeaveError: If extraction or embedding fails.

        """
        if not text or not text.strip():
            raise MemoryWeaveError("cannot add empty text to memory")

        session_id = self.config.default_session_id
        logger.debug("add() called for session %r, %d chars", session_id, len(text))

        try:
            # Step 1 — extract entities and facts
            entities, facts = self.extractor.extract(text)
            logger.debug("extracted %d entities, %d facts", len(entities), len(facts))

            # Step 2 — embed the raw text
            embedding = self.embedder.embed(text)

            # Step 3 — store in vector store
            item = MemoryItem(
                text=text,
                embedding=embedding,
                session_id=session_id,
                metadata=metadata or {},
            )
            self.store.add(item)

            # Step 4 — update knowledge graph
            if entities:
                self.graph.add_entities(entities, session_id)
            if facts:
                self.graph.add_facts(facts, session_id)

            logger.debug("add() complete — item %r stored", item.id)
            return item

        except MemoryWeaveError:
            raise
        except Exception as e:
            raise MemoryWeaveError(f"add() failed: {e}") from e

    def get(self, query: str, top_k: int | None = None) -> MemoryContext:
        """Retrieve the most relevant memories for a query.

        Runs the full retrieval pipeline:
        1. Embed the query (sentence-transformers)
        2. Search vector store for similar memories
        3. Query knowledge graph for related facts
        4. Fuse and rank results

        Args:
        ----
            query: Natural language query. Usually the user's latest message.
            top_k: Max memories to retrieve. Defaults to config.top_k.

        Returns:
        -------
            MemoryContext with summary, entries, facts, and scores.
            Inject ctx.summary into your LLM system prompt.

        Raises:
        ------
            MemoryWeaveError: If retrieval fails.

        """
        if not query or not query.strip():
            raise MemoryWeaveError("cannot search with empty query")

        k = top_k if top_k is not None else self.config.top_k
        session_id = self.config.default_session_id

        logger.debug("get() called for session %r, query=%r", session_id, query[:50])

        try:
            # Step 1 — embed the query
            query_embedding = self.embedder.embed(query)

            # Step 2 — vector store search
            vector_results = self.store.search(
                query_embedding=query_embedding,
                session_id=session_id,
                top_k=k,
            )

            # Step 3 — graph query
            graph_results = self.graph.query(
                query=query,
                session_id=session_id,
                top_k=k,
            )

            # Step 4 — fuse and rank
            context = self._ranker.fuse(
                vector_results=vector_results,
                graph_results=graph_results,
                top_k=k,
            )

            logger.debug(
                "get() complete — %d entries, %d facts retrieved",
                len(context.entries),
                len(context.facts),
            )
            return context

        except MemoryWeaveError:
            raise
        except Exception as e:
            raise MemoryWeaveError(f"get() failed: {e}") from e

    def forget(self, session_id: str | None = None) -> None:
        """Wipe all memories for a session.

        Args:
        ----
            session_id: Session to clear. Defaults to config.session_id.

        """
        sid = session_id or self.config.default_session_id
        logger.debug("forget() called for session %r", sid)

        try:
            self.store.delete_session(sid)
            self.graph.delete_session(sid)
            logger.debug("forget() complete for session %r", sid)
        except Exception as e:
            raise MemoryWeaveError(f"forget() failed: {e}") from e

    def stats(self, session_id: str | None = None) -> dict:
        """Return memory stats for a session.

        Returns
        -------
            Dict with vector_count, node_count, edge_count, session_id.

        """
        sid = session_id or self.config.default_session_id
        return {
            "session_id": sid,
            "vector_count": self.store.count(sid),
            "node_count": self.graph.node_count(sid),
            "edge_count": self.graph.edge_count(sid),
        }

    def __repr__(self) -> str:
        return (
            f"MemoryWeave(store={self.config.store_type!r}, "
            f"top_k={self.config.top_k}, "
            f"session={self.config.default_session_id!r})"
        )
