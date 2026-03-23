"""Central configuration for MemoryWeave.

Everything the client needs to know lives here. Pydantic handles
validation so we catch bad config values early instead of getting
weird errors deep in the pipeline.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """All settings for a MemoryWeave instance in one place.

    Defaults are chosen to work out of the box with zero setup —
    in-memory store, no API key, no external services needed.

    Example:
        >>> config = MemoryConfig(store_type="chroma", top_k=5)
        >>> memory = MemoryWeave(config=config)
    """

    # ── Storage ───────────────────────────────────────────────────────────────

    # "memory" is the default — nothing to install, nothing to configure.
    # swap to "chroma" or "qdrant" when you need persistence
    store_type: Literal["memory", "chroma", "qdrant"] = Field(
        default="memory",
        description="Vector store backend to use.",
    )

    # only used when store_type is chroma or qdrant
    store_path: str = Field(
        default="./memoryweave_db",
        description="Local path for persistent stores (Chroma / Qdrant).",
    )

    # ── Embedding ─────────────────────────────────────────────────────────────

    # all-MiniLM-L6-v2 is fast, small, and good enough for most use cases.
    # runs completely offline which is a big deal for privacy-conscious users
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        description="sentence-transformers model name for embedding generation.",
    )

    # ── Retrieval ─────────────────────────────────────────────────────────────

    # 5 feels right from testing — enough context without flooding the prompt.
    # users can bump this up but anything over 20 starts hurting LLM quality
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of memory results to return.",
    )

    # started with 50/50 but vector search was clearly winning on recall.
    # settled on 60/40 after benchmarking — will revisit in Phase 4
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

    # en_core_web_sm is the smallest spaCy model — fast but good enough.
    # users can swap to en_core_web_lg if they need better accuracy
    spacy_model: str = Field(
        default="en_core_web_sm",
        description="spaCy model name for NLP entity extraction.",
    )

    # ── Session ───────────────────────────────────────────────────────────────

    # single user apps can ignore session_id entirely and just use this default.
    # multi-user isolation comes in Phase 6
    default_session_id: str = Field(
        default="default",
        description="Default session namespace for memory isolation.",
    )

    # ── LLM Adapter ───────────────────────────────────────────────────────────

    # "none" means no adapter — user handles prompt injection themselves.
    # adapters are implemented in Phase 4 and handle it automatically
    llm_adapter: Literal["openai", "anthropic", "ollama", "none"] = Field(
        default="none",
        description="LLM adapter for automatic context injection.",
    )
    llm_model: str = Field(
        default="",
        description="Model name for the selected LLM adapter.",
    )

    # not storing API keys in plaintext long term — will move to env vars
    # in Phase 4 when adapters are actually implemented
    llm_api_key: str = Field(
        default="",
        description="API key for the selected LLM adapter.",
    )

    model_config = {"frozen": False}
