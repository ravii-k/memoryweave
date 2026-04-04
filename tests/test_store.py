"""Tests for the vector store — InMemoryStore and ChromaStore.

InMemoryStore tests run without any external dependencies.
ChromaStore tests require: pip install chromadb
"""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.errors import ConfigurationError
from memoryweave.store import BaseStore, ChromaStore, InMemoryStore, MemoryItem


def make_item(
    text: str = "Ravi likes Python.",
    session_id: str = "default",
    dim: int = 4,
) -> MemoryItem:
    """Create a MemoryItem with a simple fake embedding for testing."""
    embedding = [0.1 * i for i in range(dim)]
    return MemoryItem(text=text, embedding=embedding, session_id=session_id)


class TestMemoryItem:
    """Tests for the MemoryItem dataclass."""

    def test_auto_generates_id(self) -> None:
        item = make_item()
        assert item.id is not None
        assert len(item.id) > 0

    def test_custom_id(self) -> None:
        item = MemoryItem(text="Hello", embedding=[0.1], id="my-id-123")
        assert item.id == "my-id-123"

    def test_default_session(self) -> None:
        item = make_item()
        assert item.session_id == "default"

    def test_custom_session(self) -> None:
        item = make_item(session_id="user-42")
        assert item.session_id == "user-42"

    def test_empty_metadata_by_default(self) -> None:
        item = make_item()
        assert item.metadata == {}

    def test_custom_metadata(self) -> None:
        item = MemoryItem(text="Hi", embedding=[0.1], metadata={"source": "chat"})
        assert item.metadata["source"] == "chat"

    def test_repr(self) -> None:
        item = make_item()
        assert "MemoryItem" in repr(item)

    def test_equality_by_id(self) -> None:
        item1 = MemoryItem(text="Hi", embedding=[0.1], id="abc")
        item2 = MemoryItem(text="Hi", embedding=[0.1], id="abc")
        assert item1 == item2

    def test_different_ids_not_equal(self) -> None:
        item1 = make_item()
        item2 = make_item()
        assert item1 != item2


class TestBaseStoreFactory:
    """Tests for the BaseStore.create() factory method."""

    def test_creates_in_memory_store(self) -> None:
        store = BaseStore.create(MemoryConfig(store_type="memory"))
        assert isinstance(store, InMemoryStore)

    def test_creates_chroma_store(self, tmp_path: "pytest.TempPathFactory") -> None:
        config = MemoryConfig(store_type="chroma", store_path=str(tmp_path))
        store = BaseStore.create(config)
        assert isinstance(store, ChromaStore)

    def test_qdrant_raises_not_implemented(self) -> None:
        with pytest.raises(ConfigurationError, match="not yet implemented"):
            BaseStore.create(MemoryConfig(store_type="qdrant"))


class TestInMemoryStore:
    """Tests for the InMemoryStore backend."""

    @pytest.fixture
    def store(self) -> InMemoryStore:
        return InMemoryStore(MemoryConfig())

    def test_add_and_count(self, store: InMemoryStore) -> None:
        item = make_item()
        store.add(item)
        assert store.count("default") == 1

    def test_count_empty_session(self, store: InMemoryStore) -> None:
        assert store.count("nonexistent") == 0

    def test_multiple_sessions_isolated(self, store: InMemoryStore) -> None:
        store.add(make_item(session_id="user-1"))
        store.add(make_item(session_id="user-1"))
        store.add(make_item(session_id="user-2"))
        assert store.count("user-1") == 2
        assert store.count("user-2") == 1

    def test_search_returns_list(self, store: InMemoryStore) -> None:
        store.add(make_item())
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=5)
        assert isinstance(results, list)

    def test_search_returns_tuples(self, store: InMemoryStore) -> None:
        store.add(make_item())
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=5)
        assert len(results) > 0
        item, score = results[0]
        assert isinstance(item, MemoryItem)
        assert isinstance(score, float)

    def test_search_empty_session_returns_empty(self, store: InMemoryStore) -> None:
        results = store.search([0.1, 0.2, 0.3, 0.4], "empty", top_k=5)
        assert results == []

    def test_search_respects_top_k(self, store: InMemoryStore) -> None:
        for i in range(10):
            store.add(make_item(text=f"Memory {i}"))
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=3)
        assert len(results) <= 3

    def test_search_sorted_by_score_descending(self, store: InMemoryStore) -> None:
        store.add(make_item(text="A"))
        store.add(make_item(text="B"))
        store.add(make_item(text="C"))
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=5)
        scores = [score for _, score in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_session_isolation(self, store: InMemoryStore) -> None:
        store.add(make_item(session_id="user-1"))
        store.add(make_item(session_id="user-2"))
        results = store.search([0.1, 0.2, 0.3, 0.4], "user-1", top_k=5)
        for item, _ in results:
            assert item.session_id == "user-1"

    def test_delete_session(self, store: InMemoryStore) -> None:
        store.add(make_item(session_id="to-delete"))
        assert store.count("to-delete") == 1
        store.delete_session("to-delete")
        assert store.count("to-delete") == 0

    def test_delete_nonexistent_session_no_error(self, store: InMemoryStore) -> None:
        # should not raise
        store.delete_session("does-not-exist")

    def test_search_most_similar_first(self, store: InMemoryStore) -> None:
        # item with embedding [1,0,0,0] should score highest on query [1,0,0,0]
        similar = MemoryItem(
            text="Similar",
            embedding=[1.0, 0.0, 0.0, 0.0],
            session_id="default",
        )
        dissimilar = MemoryItem(
            text="Dissimilar",
            embedding=[0.0, 0.0, 0.0, 1.0],
            session_id="default",
        )
        store.add(dissimilar)
        store.add(similar)
        results = store.search([1.0, 0.0, 0.0, 0.0], "default", top_k=2)
        assert results[0][0].text == "Similar"


class TestChromaStore:
    """Tests for the ChromaStore backend.

    Uses tmp_path fixture so each test gets a clean isolated DB.
    """

    @pytest.fixture
    def store(self, tmp_path: "pytest.TempPathFactory") -> ChromaStore:
        config = MemoryConfig(store_type="chroma", store_path=str(tmp_path))
        return ChromaStore(config)

    def test_add_and_count(self, store: ChromaStore) -> None:
        item = make_item()
        store.add(item)
        assert store.count("default") == 1

    def test_count_empty_session(self, store: ChromaStore) -> None:
        assert store.count("empty-session") == 0

    def test_search_returns_results(self, store: ChromaStore) -> None:
        store.add(make_item(text="Ravi likes Python."))
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=5)
        assert len(results) > 0

    def test_search_empty_collection_returns_empty(self, store: ChromaStore) -> None:
        results = store.search([0.1, 0.2, 0.3, 0.4], "empty", top_k=5)
        assert results == []

    def test_search_returns_memory_items(self, store: ChromaStore) -> None:
        store.add(make_item())
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=5)
        item, score = results[0]
        assert isinstance(item, MemoryItem)
        assert isinstance(score, float)

    def test_delete_session(self, store: ChromaStore) -> None:
        store.add(make_item(session_id="to-delete"))
        assert store.count("to-delete") == 1
        store.delete_session("to-delete")
        assert store.count("to-delete") == 0

    def test_multiple_sessions_isolated(self, store: ChromaStore) -> None:
        store.add(make_item(session_id="user-a"))
        store.add(make_item(session_id="user-b"))
        assert store.count("user-a") == 1
        assert store.count("user-b") == 1

    def test_search_top_k_respected(self, store: ChromaStore) -> None:
        for i in range(5):
            store.add(make_item(text=f"Memory {i}"))
        results = store.search([0.1, 0.2, 0.3, 0.4], "default", top_k=3)
        assert len(results) <= 3
