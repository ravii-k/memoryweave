"""Tests for the Ranker — fusion scoring and MemoryContext building."""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.ranker import MemoryContext, Ranker
from memoryweave.store import MemoryItem


def make_item(text: str, session: str = "default") -> MemoryItem:
    return MemoryItem(text=text, embedding=[0.1, 0.2, 0.3, 0.4], session_id=session)


@pytest.fixture
def ranker() -> Ranker:
    return Ranker(MemoryConfig())


class TestMemoryContext:
    def test_default_empty(self) -> None:
        ctx = MemoryContext()
        assert ctx.summary == ""
        assert ctx.facts == []
        assert ctx.entries == []
        assert ctx.scores == []

    def test_has_results_false_when_empty(self) -> None:
        ctx = MemoryContext()
        assert ctx.has_results is False

    def test_has_results_true_with_entries(self) -> None:
        ctx = MemoryContext(entries=[(make_item("hello"), 0.9)])
        assert ctx.has_results is True

    def test_has_results_true_with_facts(self) -> None:
        ctx = MemoryContext(facts=[("Ravi likes Python", 0.8)])
        assert ctx.has_results is True

    def test_repr(self) -> None:
        ctx = MemoryContext(summary="test")
        assert "MemoryContext" in repr(ctx)


class TestRankerFuse:
    def test_empty_inputs_returns_empty_context(self, ranker: Ranker) -> None:
        ctx = ranker.fuse([], [])
        assert ctx.summary == ""
        assert not ctx.has_results

    def test_vector_only_results(self, ranker: Ranker) -> None:
        item = make_item("Ravi likes Python.")
        ctx = ranker.fuse([(item, 0.9)], [])
        assert len(ctx.entries) == 1
        assert ctx.has_results

    def test_graph_only_results(self, ranker: Ranker) -> None:
        ctx = ranker.fuse([], [("Ravi likes Python", 0.8)])
        assert len(ctx.facts) == 1
        assert ctx.has_results

    def test_returns_memory_context(self, ranker: Ranker) -> None:
        ctx = ranker.fuse([], [])
        assert isinstance(ctx, MemoryContext)

    def test_scores_populated(self, ranker: Ranker) -> None:
        item = make_item("Ravi likes Python.")
        ctx = ranker.fuse([(item, 0.9)], [])
        assert len(ctx.scores) == 1
        assert isinstance(ctx.scores[0], float)

    def test_top_k_respected(self, ranker: Ranker) -> None:
        items = [(make_item(f"Memory {i}"), 0.9 - i * 0.1) for i in range(10)]
        ctx = ranker.fuse(items, [], top_k=3)
        assert len(ctx.entries) <= 3

    def test_sorted_by_score_descending(self, ranker: Ranker) -> None:
        items = [
            (make_item("Low"), 0.3),
            (make_item("High"), 0.9),
            (make_item("Mid"), 0.6),
        ]
        ctx = ranker.fuse(items, [])
        scores = [s for _, s in ctx.entries]
        assert scores == sorted(scores, reverse=True)

    def test_summary_contains_memory_text(self, ranker: Ranker) -> None:
        item = make_item("Ravi likes Python.")
        ctx = ranker.fuse([(item, 0.9)], [])
        assert "Ravi likes Python" in ctx.summary

    def test_summary_contains_fact_text(self, ranker: Ranker) -> None:
        ctx = ranker.fuse([], [("Ravi works at Google", 0.8)])
        assert "Ravi works at Google" in ctx.summary

    def test_fusion_weights_applied(self, ranker: Ranker) -> None:
        # both vector and graph results — final score should be weighted blend
        item = make_item("Ravi likes Python.")
        ctx = ranker.fuse(
            [(item, 1.0)],
            [("Ravi likes Python", 1.0)],
        )
        assert len(ctx.entries) == 1
        # score should be at most 1.0 after fusion
        assert ctx.scores[0] <= 1.0

    def test_custom_top_k(self, ranker: Ranker) -> None:
        items = [(make_item(f"Item {i}"), float(i) / 10) for i in range(5)]
        ctx = ranker.fuse(items, [], top_k=2)
        assert len(ctx.entries) <= 2

    def test_custom_weights(self) -> None:
        # vector_weight=1.0, graph_weight=0.0 — only vector matters
        config = MemoryConfig(vector_weight=1.0, graph_weight=0.0)
        ranker = Ranker(config)
        item = make_item("Ravi likes Python.")
        ctx = ranker.fuse([(item, 0.8)], [("Ravi likes Python", 1.0)])
        # score should equal vector score * 1.0 = 0.8
        assert abs(ctx.scores[0] - 0.8) < 0.01
