"""Tests for the vector embedder.

These tests load the sentence-transformers model once per module
using a module-scoped fixture — model loading takes ~1s so we don't
want to repeat it on every test.

First run will download all-MiniLM-L6-v2 (~80MB) from HuggingFace.
Subsequent runs use the local cache and are instant.
"""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.embedder import Embedder
from memoryweave.errors import StoreError


@pytest.fixture(scope="module")
def embedder() -> Embedder:
    """Shared embedder — load model once for the whole module."""
    return Embedder(MemoryConfig())


class TestEmbedderInit:
    """Test that the Embedder loads correctly."""

    def test_loads_default_model(self) -> None:
        emb = Embedder(MemoryConfig())
        assert emb._model is not None

    def test_dimension_is_positive(self) -> None:
        emb = Embedder(MemoryConfig())
        assert emb.dimension > 0

    def test_default_model_dimension(self) -> None:
        # all-MiniLM-L6-v2 always produces 384-dim vectors
        emb = Embedder(MemoryConfig())
        assert emb.dimension == 384

    def test_invalid_model_raises_store_error(self) -> None:
        with pytest.raises(StoreError, match="failed to load"):
            Embedder(MemoryConfig(embedding_model="invalid-model-xyz-123"))


class TestEmbed:
    """Tests for the single-text embed() method."""

    def test_returns_list(self, embedder: Embedder) -> None:
        result = embedder.embed("Ravi works at Anthropic.")
        assert isinstance(result, list)

    def test_returns_floats(self, embedder: Embedder) -> None:
        result = embedder.embed("Hello world.")
        assert all(isinstance(v, float) for v in result)

    def test_correct_dimension(self, embedder: Embedder) -> None:
        result = embedder.embed("Ravi prefers Python.")
        assert len(result) == embedder.dimension

    def test_empty_text_raises(self, embedder: Embedder) -> None:
        with pytest.raises(StoreError):
            embedder.embed("")

    def test_whitespace_only_raises(self, embedder: Embedder) -> None:
        with pytest.raises(StoreError):
            embedder.embed("   ")

    def test_different_texts_give_different_vectors(self, embedder: Embedder) -> None:
        vec1 = embedder.embed("Ravi likes Python.")
        vec2 = embedder.embed("The weather is nice today.")
        assert vec1 != vec2

    def test_same_text_gives_same_vector(self, embedder: Embedder) -> None:
        text = "Ravi works at Anthropic."
        vec1 = embedder.embed(text)
        vec2 = embedder.embed(text)
        assert vec1 == vec2

    def test_similar_texts_close_vectors(self, embedder: Embedder) -> None:
        # semantically similar sentences should have high cosine similarity
        vec1 = embedder.embed("Ravi likes Python.")
        vec2 = embedder.embed("Ravi enjoys programming in Python.")
        sim = embedder.similarity(vec1, vec2)
        assert sim > 0.7, f"expected similar texts to score > 0.7, got {sim:.3f}"

    def test_dissimilar_texts_low_similarity(self, embedder: Embedder) -> None:
        vec1 = embedder.embed("Ravi works at a tech company.")
        vec2 = embedder.embed("The cat chased the mouse.")
        sim = embedder.similarity(vec1, vec2)
        assert sim < 0.9, f"expected dissimilar texts to score < 0.9, got {sim:.3f}"


class TestEmbedBatch:
    """Tests for the batch embedding method."""

    def test_returns_list_of_lists(self, embedder: Embedder) -> None:
        results = embedder.embed_batch(["Hello.", "World."])
        assert isinstance(results, list)
        assert all(isinstance(v, list) for v in results)

    def test_empty_input_returns_empty(self, embedder: Embedder) -> None:
        results = embedder.embed_batch([])
        assert results == []

    def test_correct_count(self, embedder: Embedder) -> None:
        texts = ["First.", "Second.", "Third."]
        results = embedder.embed_batch(texts)
        assert len(results) == 3

    def test_correct_dimension_per_vector(self, embedder: Embedder) -> None:
        results = embedder.embed_batch(["Hello.", "World."])
        for vec in results:
            assert len(vec) == embedder.dimension

    def test_empty_text_in_batch_raises(self, embedder: Embedder) -> None:
        with pytest.raises(StoreError):
            embedder.embed_batch(["Valid text.", "", "Another valid text."])

    def test_order_preserved(self, embedder: Embedder) -> None:
        # batch and single encode may differ by tiny float precision —
        # check similarity is near 1.0 instead of exact equality
        texts = ["Ravi likes Python.", "Ravi works at Google."]
        batch = embedder.embed_batch(texts)
        single_0 = embedder.embed(texts[0])
        single_1 = embedder.embed(texts[1])
        assert embedder.similarity(batch[0], single_0) > 0.9999
        assert embedder.similarity(batch[1], single_1) > 0.9999

    def test_single_item_batch(self, embedder: Embedder) -> None:
        results = embedder.embed_batch(["Just one sentence."])
        assert len(results) == 1
        assert len(results[0]) == embedder.dimension


class TestSimilarity:
    """Tests for the cosine similarity utility."""

    def test_identical_vectors_score_one(self, embedder: Embedder) -> None:
        vec = embedder.embed("Ravi prefers Python.")
        sim = embedder.similarity(vec, vec)
        assert abs(sim - 1.0) < 0.001

    def test_score_between_minus_one_and_one(self, embedder: Embedder) -> None:
        vec1 = embedder.embed("Python is great.")
        vec2 = embedder.embed("The sky is blue.")
        sim = embedder.similarity(vec1, vec2)
        assert -1.0 <= sim <= 1.0

    def test_dimension_mismatch_raises(self, embedder: Embedder) -> None:
        with pytest.raises(StoreError, match="dimension mismatch"):
            embedder.similarity([1.0, 2.0], [1.0, 2.0, 3.0])

    def test_symmetry(self, embedder: Embedder) -> None:
        vec1 = embedder.embed("Ravi likes Python.")
        vec2 = embedder.embed("Python is Ravi's favourite language.")
        assert (
            abs(embedder.similarity(vec1, vec2) - embedder.similarity(vec2, vec1))
            < 0.001
        )
