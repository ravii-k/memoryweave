"""Tests for MemoryWeave configuration (MemoryConfig).

These are the first real tests in the project — they verify that the
config dataclass works correctly with defaults and custom values.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

import pytest

from memoryweave.config import MemoryConfig


class TestMemoryConfigDefaults:
    """Tests that MemoryConfig defaults are sensible out of the box.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def test_default_store_type(self) -> None:
        """Default store type should be in-memory."""
        config = MemoryConfig()
        assert config.store_type == "memory"

    def test_default_top_k(self) -> None:
        """Default top_k should be 5."""
        config = MemoryConfig()
        assert config.top_k == 5

    def test_default_session_id(self) -> None:
        """Default session ID should be 'default'."""
        config = MemoryConfig()
        assert config.default_session_id == "default"

    def test_default_embedding_model(self) -> None:
        """Default embedding model should be all-MiniLM-L6-v2."""
        config = MemoryConfig()
        assert config.embedding_model == "all-MiniLM-L6-v2"

    def test_default_weights_sum_to_one(self) -> None:
        """Vector + graph weights should sum to 1.0 by default."""
        config = MemoryConfig()
        assert config.vector_weight + config.graph_weight == pytest.approx(1.0)

    def test_default_llm_adapter(self) -> None:
        """Default LLM adapter should be 'none' (no adapter)."""
        config = MemoryConfig()
        assert config.llm_adapter == "none"


class TestMemoryConfigCustomValues:
    """Tests that MemoryConfig accepts valid custom values.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def test_custom_store_type_chroma(self) -> None:
        """Should accept 'chroma' as a store type."""
        config = MemoryConfig(store_type="chroma")
        assert config.store_type == "chroma"

    def test_custom_store_type_qdrant(self) -> None:
        """Should accept 'qdrant' as a store type."""
        config = MemoryConfig(store_type="qdrant")
        assert config.store_type == "qdrant"

    def test_custom_top_k(self) -> None:
        """Should accept valid top_k values."""
        config = MemoryConfig(top_k=10)
        assert config.top_k == 10

    def test_custom_session_id(self) -> None:
        """Should accept a custom default session ID."""
        config = MemoryConfig(default_session_id="user-123")
        assert config.default_session_id == "user-123"

    def test_custom_weights(self) -> None:
        """Should accept custom fusion weights."""
        config = MemoryConfig(vector_weight=0.7, graph_weight=0.3)
        assert config.vector_weight == pytest.approx(0.7)
        assert config.graph_weight == pytest.approx(0.3)

    def test_openai_adapter(self) -> None:
        """Should accept 'openai' as an LLM adapter."""
        config = MemoryConfig(llm_adapter="openai", llm_model="gpt-4o")
        assert config.llm_adapter == "openai"
        assert config.llm_model == "gpt-4o"


class TestMemoryConfigValidation:
    """Tests that MemoryConfig rejects invalid values.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def test_invalid_store_type(self) -> None:
        """Should raise a validation error for unknown store types."""
        with pytest.raises(Exception):
            MemoryConfig(store_type="invalid_store")  # type: ignore

    def test_top_k_too_low(self) -> None:
        """Should raise a validation error if top_k < 1."""
        with pytest.raises(Exception):
            MemoryConfig(top_k=0)

    def test_top_k_too_high(self) -> None:
        """Should raise a validation error if top_k > 50."""
        with pytest.raises(Exception):
            MemoryConfig(top_k=51)

    def test_weight_out_of_range(self) -> None:
        """Should raise a validation error if weight > 1.0."""
        with pytest.raises(Exception):
            MemoryConfig(vector_weight=1.5)
