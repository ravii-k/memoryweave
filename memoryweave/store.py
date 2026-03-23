"""Vector store abstraction — unified interface for all storage backends.

Defines the BaseStore interface and a factory method. Concrete
implementations (Chroma, Qdrant, in-memory) are registered here.

Full implementation: Phase 3, Chapter 3.2.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from memoryweave.config import MemoryConfig


class MemoryItem:
    """A single memory item stored in the vector store.

    Attributes:
        id: Unique identifier for this memory item.
        text: Original raw text this memory was created from.
        embedding: Dense vector representation of the text.
        session_id: Session namespace this memory belongs to.
        metadata: Arbitrary key-value metadata (timestamps, source, etc.)

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(
        self,
        id: str,
        text: str,
        embedding: list[float],
        session_id: str = "default",
        metadata: dict | None = None,
    ) -> None:
        """Initialise a MemoryItem.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.id = id
        self.text = text
        self.embedding = embedding
        self.session_id = session_id
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        return f"MemoryItem(id={self.id!r}, session={self.session_id!r})"


class BaseStore(ABC):
    """Abstract base class for all vector store backends.

    All concrete stores (Chroma, Qdrant, in-memory) must implement
    these methods. This ensures the client code never depends on a
    specific backend — swap backends via MemoryConfig with zero code change.

    Full implementation: Phase 3, Chapter 3.2.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    @abstractmethod
    def add(self, item: MemoryItem) -> None:
        """Store a single MemoryItem.

        Args:
            item: The memory item to store.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        session_id: str,
        top_k: int,
    ) -> list[tuple[MemoryItem, float]]:
        """Search for the most similar memories by embedding.

        Args:
            query_embedding: Dense vector of the search query.
            session_id: Session namespace to search within.
            top_k: Maximum number of results to return.

        Returns:
            List of (MemoryItem, score) tuples, sorted by score descending.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete all memories for a session.

        Args:
            session_id: Session namespace to clear.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """

    @classmethod
    def create(cls, config: MemoryConfig) -> "BaseStore":
        """Factory method — create the correct store from config.

        Args:
            config: MemoryConfig controlling which backend to create.

        Returns:
            A concrete BaseStore instance.

        Raises:
            ConfigurationError: If store_type is not recognised.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Wire up backends in Phase 3, Ch 3.2.
        # if config.store_type == "memory":
        #     return InMemoryStore(config)
        # elif config.store_type == "chroma":
        #     return ChromaStore(config)
        # elif config.store_type == "qdrant":
        #     return QdrantStore(config)
        raise NotImplementedError(
            "BaseStore.create() will be implemented in Phase 3, Chapter 3.2."
        )
