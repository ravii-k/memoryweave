"""Tests for the MemoryWeave client — end-to-end pipeline tests.

These tests load spaCy and sentence-transformers so they're slower.
Using module-scoped fixtures to keep total time reasonable.
"""

from __future__ import annotations

import pytest

from memoryweave.client import MemoryWeave
from memoryweave.config import MemoryConfig
from memoryweave.errors import MemoryWeaveError
from memoryweave.ranker import MemoryContext
from memoryweave.store import MemoryItem


@pytest.fixture(scope="module")
def memory() -> MemoryWeave:
    """Shared MemoryWeave instance — loads models once per module."""
    return MemoryWeave(MemoryConfig())


class TestMemoryWeaveInit:
    def test_default_init(self) -> None:
        m = MemoryWeave()
        assert m.config is not None

    def test_custom_config(self) -> None:
        config = MemoryConfig(top_k=3)
        m = MemoryWeave(config)
        assert m.config.top_k == 3

    def test_repr(self) -> None:
        m = MemoryWeave()
        assert "MemoryWeave" in repr(m)
        assert "store=" in repr(m)

    def test_lazy_init_extractor(self) -> None:
        m = MemoryWeave()
        assert m._extractor is None
        # access triggers load
        _ = m.extractor
        assert m._extractor is not None

    def test_lazy_init_embedder(self) -> None:
        m = MemoryWeave()
        assert m._embedder is None
        _ = m.embedder
        assert m._embedder is not None


class TestAdd:
    def test_returns_memory_item(self, memory: MemoryWeave) -> None:
        item = memory.add("Ravi works at Anthropic.")
        assert isinstance(item, MemoryItem)

    def test_item_has_text(self, memory: MemoryWeave) -> None:
        item = memory.add("Ravi likes Python.")
        assert item.text == "Ravi likes Python."

    def test_item_has_id(self, memory: MemoryWeave) -> None:
        item = memory.add("Ravi lives in India.")
        assert item.id is not None

    def test_item_has_embedding(self, memory: MemoryWeave) -> None:
        item = memory.add("Ravi prefers dark mode.")
        assert len(item.embedding) == 384

    def test_empty_text_raises(self, memory: MemoryWeave) -> None:
        with pytest.raises(MemoryWeaveError):
            memory.add("")

    def test_whitespace_raises(self, memory: MemoryWeave) -> None:
        with pytest.raises(MemoryWeaveError):
            memory.add("   ")

    def test_increments_store_count(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="count-test"))
        before = m.store.count("count-test")
        m.add("Test memory.")
        after = m.store.count("count-test")
        assert after == before + 1

    def test_custom_metadata(self, memory: MemoryWeave) -> None:
        item = memory.add("Test with metadata.", metadata={"source": "test"})
        assert item.metadata["source"] == "test"


class TestGet:
    def test_returns_memory_context(self, memory: MemoryWeave) -> None:
        memory.add("Ravi prefers Python over JavaScript.")
        ctx = memory.get("What language does Ravi prefer?")
        assert isinstance(ctx, MemoryContext)

    def test_has_results_after_add(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="get-test"))
        m.add("Ravi likes Python.")
        ctx = m.get("Python")
        assert ctx.has_results

    def test_summary_is_string(self, memory: MemoryWeave) -> None:
        ctx = memory.get("What does Ravi like?")
        assert isinstance(ctx.summary, str)

    def test_empty_query_raises(self, memory: MemoryWeave) -> None:
        with pytest.raises(MemoryWeaveError):
            memory.get("")

    def test_whitespace_query_raises(self, memory: MemoryWeave) -> None:
        with pytest.raises(MemoryWeaveError):
            memory.get("   ")

    def test_empty_store_returns_empty_context(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="empty-session-xyz"))
        ctx = m.get("anything")
        assert isinstance(ctx, MemoryContext)

    def test_top_k_respected(self) -> None:
        m = MemoryWeave(MemoryConfig(default_default_session_id="topk-test", top_k=2))
        for i in range(5):
            m.add(f"Memory number {i} about Python and coding.")
        ctx = m.get("Python", top_k=2)
        assert len(ctx.entries) <= 2


class TestForget:
    def test_forget_clears_store(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="forget-test"))
        m.add("Remember this.")
        assert m.store.count("forget-test") == 1
        m.forget()
        assert m.store.count("forget-test") == 0

    def test_forget_clears_graph(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="forget-graph-test"))
        m.add("Ravi likes Python.")
        m.forget()
        assert m.graph.node_count("forget-graph-test") == 0

    def test_forget_custom_session(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="main-session"))
        m.add("Keep this.")
        m.forget(session_id="other-session")
        # main session should be untouched
        assert m.store.count("main-session") == 1


class TestStats:
    def test_returns_dict(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="stats-test"))
        stats = m.stats()
        assert isinstance(stats, dict)

    def test_stats_has_required_keys(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="stats-keys-test"))
        stats = m.stats()
        assert "session_id" in stats
        assert "vector_count" in stats
        assert "node_count" in stats
        assert "edge_count" in stats

    def test_stats_increments_after_add(self) -> None:
        m = MemoryWeave(MemoryConfig(default_session_id="stats-count-test"))
        assert m.stats()["vector_count"] == 0
        m.add("Ravi likes Python.")
        assert m.stats()["vector_count"] == 1


class TestDeduplication:
    @pytest.fixture
    def fresh(self) -> MemoryWeave:
        """Fresh isolated memory instance for dedup tests."""
        return MemoryWeave(MemoryConfig(default_session_id="dedup-isolated"))

    def test_duplicate_text_not_stored_twice(self, fresh: MemoryWeave) -> None:
        fresh.add("Ravi prefers Python for everything.")
        fresh.add("Ravi prefers Python for everything.")
        assert fresh.stats()["vector_count"] == 1

    def test_similar_but_not_identical_is_stored(self, fresh: MemoryWeave) -> None:
        fresh.add("Ravi prefers Python.")
        fresh.add("Ravi loves JavaScript.")
        assert fresh.stats()["vector_count"] == 2


class TestAsyncMethods:
    @pytest.mark.asyncio
    async def test_async_add_returns_item(self, memory: MemoryWeave) -> None:
        item = await memory.async_add("Ravi uses async Python.")
        assert item.text == "Ravi uses async Python."

    @pytest.mark.asyncio
    async def test_async_get_returns_context(self, memory: MemoryWeave) -> None:
        await memory.async_add("Ravi likes FastAPI.")
        ctx = await memory.async_get("What framework?")
        assert ctx.has_results

    @pytest.mark.asyncio
    async def test_async_forget_clears_store(self, memory: MemoryWeave) -> None:
        await memory.async_add("Temporary memory.")
        await memory.async_forget()
        assert memory.stats()["vector_count"] == 0
