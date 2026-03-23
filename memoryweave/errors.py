"""MemoryWeave custom exception classes.

All errors raised by the MemoryWeave SDK inherit from MemoryWeaveError
so users can catch them with a single except clause if needed.

    >>> try:
    ...     memory.add("")
    ... except memoryweave.errors.MemoryWeaveError as e:
    ...     print(e)

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""


class MemoryWeaveError(Exception):
    """Base exception for all MemoryWeave errors.

    Catch this to handle any MemoryWeave-specific error in one place.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class ConfigurationError(MemoryWeaveError):
    """Raised when the MemoryConfig contains invalid or missing values.

    Example:
        Raised if vector_weight + graph_weight != 1.0, or if an
        unsupported store_type is provided.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class ExtractionError(MemoryWeaveError):
    """Raised when the NLP pipeline fails to process input text.

    Example:
        Raised if spaCy model is not installed or text is empty.
        Will be used in Phase 2, Chapter 2.1.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class StoreError(MemoryWeaveError):
    """Raised when a vector store operation fails.

    Example:
        Raised on ChromaDB connection failure or Qdrant timeout.
        Will be used in Phase 3, Chapter 3.2.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class GraphError(MemoryWeaveError):
    """Raised when a knowledge graph operation fails.

    Example:
        Raised if a graph query returns malformed data.
        Will be used in Phase 3, Chapter 3.3.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class AdapterError(MemoryWeaveError):
    """Raised when an LLM adapter call fails.

    Example:
        Raised on OpenAI API timeout or invalid API key.
        Will be used in Phase 4, Chapter 4.3.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """


class SessionError(MemoryWeaveError):
    """Raised when a session operation fails.

    Example:
        Raised if a session_id references a deleted session.
        Will be used in Phase 6, Chapter 6.2.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """
