"""Vector store abstraction — one interface, multiple backends.

Three backends:
- InMemoryStore  — default, zero setup, no persistence (great for dev/testing)
- ChromaStore    — local persistence, easy to self-host
- QdrantStore    — stub, implemented in Phase 6

All three share the same BaseStore interface so swapping backends
is just a config change — no code change needed.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from memoryweave.config import MemoryConfig
from memoryweave.errors import ConfigurationError, StoreError
from memoryweave.logger import get_logger

logger = get_logger(__name__)


class MemoryItem:
    """A single memory item stored in the vector store.

    Wraps the raw text, its embedding, and metadata together.
    The metadata dict is flexible — callers can store timestamps,
    source info, importance scores, whatever they need.

    Attributes
    ----------
        id: Unique ID for this memory. UUIDs by default.
        text: The original raw text this memory was built from.
        embedding: Dense vector representation of the text.
        session_id: Which user/session this memory belongs to.
        metadata: Freeform key-value store for extra info.

    """

    def __init__(
        self,
        text: str,
        embedding: list[float],
        session_id: str = "default",
        metadata: dict | None = None,
        id: str | None = None,
    ) -> None:
        # auto-generate UUID if no id provided
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.embedding = embedding
        self.session_id = session_id
        # using None default to avoid the mutable default argument trap
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"MemoryItem(id={self.id!r}, session={self.session_id!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemoryItem):
            return NotImplemented
        return self.id == other.id


class BaseStore(ABC):
    """Abstract interface that all vector store backends must implement.

    Keeping the interface minimal — add(), search(), delete_session(),
    count(). Anything fancier lives in the concrete classes.
    """

    @abstractmethod
    def add(self, item: MemoryItem) -> None:
        """Store a single MemoryItem."""

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
    ) -> list[tuple[MemoryItem, float]]:
        """Find the most similar memories by cosine similarity.

        Args:
        ----
            query_embedding: Dense vector of the search query.
            session_id: Only search within this session's memories.
            top_k: Maximum number of results to return.

        Returns:
        -------
            List of (MemoryItem, score) tuples, best match first.
            Score is cosine similarity — higher is more relevant.

        """

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Wipe all memories for a given session."""

    @abstractmethod
    def count(self, session_id: str) -> int:
        """Return the number of memories stored for a session."""

    @classmethod
    def create(cls, config: MemoryConfig) -> "BaseStore":
        """Pick the right backend from config and return a ready store instance.

        Args:
        ----
            config: MemoryConfig with store_type set.

        Returns:
        -------
            A concrete BaseStore instance ready to use.

        Raises:
        ------
            ConfigurationError: If store_type is not recognised.

        """
        if config.store_type == "memory":
            logger.debug("creating InMemoryStore")
            return InMemoryStore(config)
        elif config.store_type == "chroma":
            logger.debug("creating ChromaStore at %r", config.store_path)
            return ChromaStore(config)
        elif config.store_type == "qdrant":
            # QdrantStore comes in Phase 6
            raise ConfigurationError(
                "Qdrant store is not yet implemented. Use store_type='memory' or 'chroma' for now."
            )
        else:
            raise ConfigurationError(
                f"Unknown store_type {config.store_type!r}. "
                "Choose from: 'memory', 'chroma', 'qdrant'."
            )


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Returns a value between -1.0 and 1.0. Used by InMemoryStore
    for search scoring.
    """
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryStore(BaseStore):
    """In-process vector store — zero setup, no persistence.

    Stores everything in a plain Python list and does brute-force
    cosine similarity search. Fast enough for hundreds of memories.
    For thousands of memories, switch to ChromaDB.

    Data is lost when the process exits — this is intentional.
    It's the right default for development and testing.
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        # dict of session_id -> list of MemoryItem
        self._store: dict[str, list[MemoryItem]] = {}

    def add(self, item: MemoryItem) -> None:
        """Add a MemoryItem to the in-memory store."""
        if item.session_id not in self._store:
            self._store[item.session_id] = []
        self._store[item.session_id].append(item)
        logger.debug(
            "InMemoryStore: added item %r to session %r",
            item.id,
            item.session_id,
        )

    def search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
    ) -> list[tuple[MemoryItem, float]]:
        """Brute-force cosine similarity search over all session items."""
        items = self._store.get(session_id, [])
        if not items:
            return []

        # score every item
        scored = [(item, _cosine_similarity(query_embedding, item.embedding)) for item in items]

        # sort by score descending and return top_k
        scored.sort(key=lambda x: x[1], reverse=True)
        results = scored[:top_k]

        logger.debug(
            "InMemoryStore: search returned %d/%d results for session %r",
            len(results),
            len(items),
            session_id,
        )
        return results

    def delete_session(self, session_id: str) -> None:
        """Wipe all memories for a session."""
        deleted = len(self._store.pop(session_id, []))
        logger.debug(
            "InMemoryStore: deleted %d items from session %r",
            deleted,
            session_id,
        )

    def count(self, session_id: str) -> int:
        """Return the number of memories stored for a session."""
        return len(self._store.get(session_id, []))


class ChromaStore(BaseStore):
    """ChromaDB-backed vector store with local persistence.

    Data persists to disk at config.store_path. ChromaDB handles
    embedding storage and ANN search internally.

    Requires: pip install chromadb
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        self._client = self._init_client(config.store_path)

    def _init_client(self, path: str) -> "Any":
        """Initialise ChromaDB persistent client."""
        try:
            import chromadb

            client = chromadb.PersistentClient(path=path)
            logger.debug("ChromaStore: connected to %r", path)
            return client
        except ImportError as e:
            raise StoreError(
                "ChromaDB is not installed. Install it with: pip install chromadb"
            ) from e
        except Exception as e:
            raise StoreError(f"Failed to connect to ChromaDB at {path!r}: {e}") from e

    def _get_collection(self, session_id: str) -> "Any":
        """Get or create a ChromaDB collection for the session.

        Each session gets its own isolated collection. Collection names
        must be alphanumeric so we sanitise the session_id.
        """
        # chromadb collection names: alphanumeric and hyphens only
        safe_name = f"mw-{session_id}".replace("_", "-").replace(" ", "-")
        return self._client.get_or_create_collection(
            name=safe_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(self, item: MemoryItem) -> None:
        """Add a MemoryItem to the ChromaDB collection for its session."""
        try:
            collection = self._get_collection(item.session_id)
            collection.add(
                ids=[item.id],
                embeddings=[item.embedding],
                documents=[item.text],
                metadatas=[{**item.metadata, "session_id": item.session_id}],
            )
            logger.debug(
                "ChromaStore: added item %r to session %r",
                item.id,
                item.session_id,
            )
        except Exception as e:
            raise StoreError(f"ChromaDB add failed: {e}") from e

    def search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
    ) -> list[tuple[MemoryItem, float]]:
        """ANN search using ChromaDB's built-in HNSW index."""
        try:
            collection = self._get_collection(session_id)

            if collection.count() == 0:
                return []

            actual_top_k = min(top_k, collection.count())
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=actual_top_k,
                include=["documents", "metadatas", "distances", "embeddings"],
            )

            items = []
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]
                embedding = results["embeddings"][0][i]
                # chromadb returns distances (lower = more similar)
                # convert to similarity score (higher = more similar)
                distance = results["distances"][0][i]
                score = 1.0 - distance

                item = MemoryItem(
                    id=doc_id,
                    text=document,
                    embedding=list(embedding),
                    session_id=metadata.get("session_id", session_id),
                    metadata={k: v for k, v in metadata.items() if k != "session_id"},
                )
                items.append((item, float(score)))

            logger.debug(
                "ChromaStore: search returned %d results for session %r",
                len(items),
                session_id,
            )
            return items

        except Exception as e:
            raise StoreError(f"ChromaDB search failed: {e}") from e

    def delete_session(self, session_id: str) -> None:
        """Delete the ChromaDB collection for this session."""
        try:
            safe_name = f"mw-{session_id}".replace("_", "-").replace(" ", "-")
            self._client.delete_collection(name=safe_name)
            logger.debug("ChromaStore: deleted collection for session %r", session_id)
        except Exception as e:
            raise StoreError(f"ChromaDB delete_session failed: {e}") from e

    def count(self, session_id: str) -> int:
        """Return the number of memories stored for a session."""
        try:
            collection = self._get_collection(session_id)
            return collection.count()
        except Exception as e:
            raise StoreError(f"ChromaDB count failed: {e}") from e
