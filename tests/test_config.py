"""Tests for MemoryConfig.

Covering three things:
1. Defaults are sensible out of the box
2. Custom values get stored correctly
3. Invalid values get rejected by Pydantic validation

These are the first real tests in the project so keeping them
straightforward — no mocking, no fixtures, just direct instantiation.
"""

import pytest

from memoryweave.config import MemoryConfig


class TestMemoryConfigDefaults:
    """Make sure the defaults work without any config at all."""

    def test_default_store_type(self) -> None:
        """In-memory store is the default — zero setup required."""
        config = MemoryConfig()
        assert config.store_type == "memory"

    def test_default_top_k(self) -> None:
        """5 results feels right — enough context without flooding the prompt."""
        config = MemoryConfig()
        assert config.top_k == 5

    def test_default_session_id(self) -> None:
        """Single-user apps can ignore session_id entirely."""
        config = MemoryConfig()
        assert config.default_session_id == "default"

    def test_default_embedding_model(self) -> None:
        """all-MiniLM-L6-v2 — fast, offline, good enough for most cases."""
        config = MemoryConfig()
        assert config.embedding_model == "all-MiniLM-L6-v2"

    def test_default_weights_sum_to_one(self) -> None:
        """Vector + graph weights should always sum to 1.0."""
        config = MemoryConfig()
        assert config.vector_weight + config.graph_weight == pytest.approx(1.0)

    def test_default_llm_adapter(self) -> None:
        """No adapter by default — users handle injection themselves."""
        config = MemoryConfig()
        assert config.llm_adapter == "none"


class TestMemoryConfigCustomValues:
    """Make sure custom values get stored and returned correctly."""

    def test_custom_store_type_chroma(self) -> None:
        config = MemoryConfig(store_type="chroma")
        assert config.store_type == "chroma"

    def test_custom_store_type_qdrant(self) -> None:
        config = MemoryConfig(store_type="qdrant")
        assert config.store_type == "qdrant"

    def test_custom_top_k(self) -> None:
        config = MemoryConfig(top_k=10)
        assert config.top_k == 10

    def test_custom_session_id(self) -> None:
        config = MemoryConfig(default_session_id="user-123")
        assert config.default_session_id == "user-123"

    def test_custom_weights(self) -> None:
        config = MemoryConfig(vector_weight=0.7, graph_weight=0.3)
        assert config.vector_weight == pytest.approx(0.7)
        assert config.graph_weight == pytest.approx(0.3)

    def test_openai_adapter(self) -> None:
        config = MemoryConfig(llm_adapter="openai", llm_model="gpt-4o")
        assert config.llm_adapter == "openai"
        assert config.llm_model == "gpt-4o"


class TestMemoryConfigValidation:
    """Pydantic should reject bad values loudly, not silently accept them."""

    def test_invalid_store_type(self) -> None:
        """Should blow up if someone passes an unsupported store backend."""
        with pytest.raises(Exception):
            MemoryConfig(store_type="invalid_store")  # type: ignore

    def test_top_k_too_low(self) -> None:
        """top_k of 0 makes no sense — at least 1 result required."""
        with pytest.raises(Exception):
            MemoryConfig(top_k=0)

    def test_top_k_too_high(self) -> None:
        """Anything above 50 would flood the prompt — capping it here."""
        with pytest.raises(Exception):
            MemoryConfig(top_k=51)

    def test_weight_out_of_range(self) -> None:
        """Weights must be between 0 and 1 — they're percentages."""
        with pytest.raises(Exception):
            MemoryConfig(vector_weight=1.5)
