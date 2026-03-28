"""Vector store abstraction — one interface, multiple backends.

The idea is simple: the rest of the codebase never talks to ChromaDB
or Qdrant directly. Everything goes through BaseStore. That way swapping
backends is just a config change, not a code change.

Three backends planned:
- InMemoryStore  — default, zero setup, no persistence (good for dev/testing)
- ChromaStore    — local persistence, easy to self-host
- QdrantStore    — production-grade, good for scale

All three get implemented in Phase 3, Chapter 3.2.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from memoryweave.config import MemoryConfig


class MemoryItem:
    """A single memory item stored in the vector store.

    Wraps the raw text, its embedding, and some metadata together.
    The metadata dict is flexible — callers can store timestamps,
    source info, importance scores, whatever they need.

    Attributes:
        id: Unique ID for this memory. Using UUIDs in the implementation.
        text: The original raw text this memory was built from.
        embedding: Dense vector representation of the text.
        session_id: Which user/session this memory belongs to.
        metadata: Freeform key-value store for extra info.
    """

    def __init__(
        self,
        id: str,
        text: str,
        embedding: list[float],
        session_id: str = "default",
        metadata: dict | None = None,
    ) -> None:
        self.id = id
        self.text = text
        self.embedding = embedding
        self.session_id = session_id
        # using None default to avoid the mutable default argument trap
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"MemoryItem(id={self.id!r}, session={self.session_id!r})"


class BaseStore(ABC):
    """Abstract interface for all vector store backends.

    Every backend must implement these three methods. The factory
    method at the bottom handles choosing the right one from config.

    Keeping the interface minimal on purpose — add(), search(),
    delete_session(). Anything fancier can go in the concrete classes.
    """

    @abstractmethod
    def add(self, item: MemoryItem) -> None:
        """Store a single MemoryItem.

        Args:
            item: The memory item to store, including its embedding.
        """

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
    ) -> list[tuple[MemoryItem, float]]:
        """Find the most similar memories by embedding distance.

        Args:
            query_embedding: Dense vector of the search query.
            session_id: Only search within this session's memories.
            top_k: How many results to return.

        Returns:
            List of (MemoryItem, score) tuples, best match first.
            Score is cosine similarity — higher is more relevant.
        """

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Wipe all memories for a given session.

        Args:
            session_id: The session to clear completely.
        """

    @classmethod
    def create(cls, config: MemoryConfig) -> "BaseStore":
        """Factory — picks the right backend from the config.

        Args:
            config: MemoryConfig with store_type set.

        Returns:
            A concrete BaseStore instance ready to use.

        Raises:
            ConfigurationError: If store_type isn't recognised.
        """
        # will wire up all three backends in Phase 3, Chapter 3.2.
        # the pattern will be a simple if/elif on config.store_type
        # if config.store_type == "memory":
        #     return InMemoryStore(config)
        # elif config.store_type == "chroma":
        #     return ChromaStore(config)
        # elif config.store_type == "qdrant":
        #     return QdrantStore(config)
        raise NotImplementedError("coming in Phase 3, Chapter 3.2")
