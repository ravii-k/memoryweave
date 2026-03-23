"""MemoryWeave configuration dataclass.

All settings for the MemoryWeave client are defined here.
Users pass a MemoryConfig instance when creating a MemoryWeave client,
or rely on sensible defaults.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """Central configuration for a MemoryWeave instance.

    All fields have sensible defaults so the client works out of the
    box with zero configuration.

    Example:
        >>> config = MemoryConfig(store_type="chroma", top_k=5)
        >>> memory = MemoryWeave(config=config)

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    # ── Storage ───────────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - "memory" = in-process, no persistence.
    # "chroma" and "qdrant" will be wired up in Phase 3, Chapter 3.2.
    store_type: Literal["memory", "chroma", "qdrant"] = Field(
        default="memory",
        description="Vector store backend to use.",
    )
    store_path: str = Field(
        default="./memoryweave_db",
        description="Local path for persistent stores (Chroma / Qdrant).",
    )

    # ── Embedding ─────────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - Default model runs fully offline (no API key).
    # Will be used in Phase 3, Chapter 3.1.
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="sentence-transformers model name for embedding generation.",
    )

    # ── Retrieval ─────────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - Number of memories returned by memory.get().
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of memory results to return.",
    )

    # [Ravi Kashyap] 2026-03-23 - Fusion weights for vector + graph scores.
    # Must sum to 1.0. Benchmarked in docs/context-ranker.md (Phase 4).
    vector_weight: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Weight of vector search score in final ranking (0.0–1.0).",
    )
    graph_weight: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Weight of knowledge graph score in final ranking (0.0–1.0).",
    )

    # ── NLP ───────────────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - spaCy model used for entity extraction.
    # Will be used in Phase 2, Chapter 2.1.
    spacy_model: str = Field(
        default="en_core_web_sm",
        description="spaCy model name for NLP entity extraction.",
    )

    # ── Session ───────────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - Default session ID for single-user usage.
    # Multi-user session isolation is added in Phase 6, Chapter 6.2.
    default_session_id: str = Field(
        default="default",
        description="Default session namespace for memory isolation.",
    )

    # ── LLM Adapter ───────────────────────────────────────────────────────────
    # [Ravi Kashyap] 2026-03-23 - Which LLM adapter to use.
    # Adapters are implemented in Phase 4, Chapter 4.3.
    llm_adapter: Literal["openai", "anthropic", "ollama", "none"] = Field(
        default="none",
        description="LLM adapter for automatic context injection.",
    )
    llm_model: str = Field(
        default="",
        description="Model name for the selected LLM adapter.",
    )
    llm_api_key: str = Field(
        default="",
        description="API key for the selected LLM adapter.",
    )

    model_config = {"frozen": False}
