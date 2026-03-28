"""Tests for MemoryConfig."""

import pytest

from memoryweave.config import MemoryConfig


class TestMemoryConfigDefaults:
    def test_default_store_type(self):
        assert MemoryConfig().store_type == "memory"

    def test_default_top_k(self):
        assert MemoryConfig().top_k == 5

    def test_default_session_id(self):
        assert MemoryConfig().default_session_id == "default"

    def test_default_embedding_model(self):
        assert MemoryConfig().embedding_model == "all-MiniLM-L6-v2"

    def test_default_weights_sum_to_one(self):
        c = MemoryConfig()
        assert c.vector_weight + c.graph_weight == pytest.approx(1.0)

    def test_default_llm_adapter(self):
        assert MemoryConfig().llm_adapter == "none"


class TestMemoryConfigCustomValues:
    def test_custom_store_type_chroma(self):
        assert MemoryConfig(store_type="chroma").store_type == "chroma"

    def test_custom_store_type_qdrant(self):
        assert MemoryConfig(store_type="qdrant").store_type == "qdrant"

    def test_custom_top_k(self):
        assert MemoryConfig(top_k=10).top_k == 10

    def test_custom_session_id(self):
        assert (
            MemoryConfig(default_session_id="user-123").default_session_id == "user-123"
        )

    def test_custom_weights(self):
        c = MemoryConfig(vector_weight=0.7, graph_weight=0.3)
        assert c.vector_weight == pytest.approx(0.7)
        assert c.graph_weight == pytest.approx(0.3)

    def test_openai_adapter(self):
        c = MemoryConfig(llm_adapter="openai", llm_model="gpt-4o")
        assert c.llm_adapter == "openai"
        assert c.llm_model == "gpt-4o"


class TestMemoryConfigValidation:
    def test_invalid_store_type(self):
        with pytest.raises(Exception):
            MemoryConfig(store_type="invalid_store")

    def test_top_k_too_low(self):
        with pytest.raises(Exception):
            MemoryConfig(top_k=0)

    def test_top_k_too_high(self):
        with pytest.raises(Exception):
            MemoryConfig(top_k=51)

    def test_weight_out_of_range(self):
        with pytest.raises(Exception):
            MemoryConfig(vector_weight=1.5)

    def test_weights_must_sum_to_one(self):
        with pytest.raises(Exception):
            MemoryConfig(vector_weight=0.9, graph_weight=0.9)
