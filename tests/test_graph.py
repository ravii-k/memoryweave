"""Tests for the KnowledgeGraph — Chapter 3.3.

Tests cover entity/fact insertion, querying, session isolation,
persistence (save/load), and edge cases.
"""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.errors import GraphError
from memoryweave.extractor import EntityResult, FactResult
from memoryweave.graph import KnowledgeGraph


@pytest.fixture
def kg() -> KnowledgeGraph:
    """Fresh KnowledgeGraph for each test."""
    return KnowledgeGraph(MemoryConfig())


def make_entity(text: str, label: str = "PERSON") -> EntityResult:
    return EntityResult(text=text, label=label)


def make_fact(subject: str, predicate: str, obj: str) -> FactResult:
    return FactResult(subject=subject, predicate=predicate, obj=obj)


class TestKnowledgeGraphInit:
    def test_starts_empty(self, kg: KnowledgeGraph) -> None:
        assert kg.node_count("default") == 0
        assert kg.edge_count("default") == 0


class TestAddEntities:
    def test_adds_single_entity(self, kg: KnowledgeGraph) -> None:
        kg.add_entities([make_entity("Ravi", "PERSON")], "default")
        assert kg.node_count("default") == 1

    def test_adds_multiple_entities(self, kg: KnowledgeGraph) -> None:
        entities = [
            make_entity("Ravi", "PERSON"),
            make_entity("Google", "ORG"),
            make_entity("India", "GPE"),
        ]
        kg.add_entities(entities, "default")
        assert kg.node_count("default") == 3

    def test_no_duplicate_nodes(self, kg: KnowledgeGraph) -> None:
        entity = make_entity("Ravi", "PERSON")
        kg.add_entities([entity], "default")
        kg.add_entities([entity], "default")
        assert kg.node_count("default") == 1

    def test_empty_list_no_error(self, kg: KnowledgeGraph) -> None:
        kg.add_entities([], "default")
        assert kg.node_count("default") == 0

    def test_session_isolation(self, kg: KnowledgeGraph) -> None:
        kg.add_entities([make_entity("Ravi")], "user-1")
        kg.add_entities([make_entity("Alex")], "user-2")
        assert kg.node_count("user-1") == 1
        assert kg.node_count("user-2") == 1


class TestAddFacts:
    def test_adds_single_fact(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "works", "Google")], "default")
        assert kg.edge_count("default") == 1

    def test_adds_multiple_facts(self, kg: KnowledgeGraph) -> None:
        facts = [
            make_fact("Ravi", "works", "Google"),
            make_fact("Ravi", "likes", "Python"),
            make_fact("Ravi", "lives", "India"),
        ]
        kg.add_facts(facts, "default")
        assert kg.edge_count("default") == 3

    def test_auto_creates_nodes_for_facts(self, kg: KnowledgeGraph) -> None:
        # adding a fact should auto-create subject and object nodes
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        assert kg.node_count("default") == 2

    def test_empty_list_no_error(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([], "default")
        assert kg.edge_count("default") == 0

    def test_session_isolation(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "user-1")
        kg.add_facts([make_fact("Alex", "likes", "Rust")], "user-2")
        assert kg.edge_count("user-1") == 1
        assert kg.edge_count("user-2") == 1


class TestQuery:
    def test_returns_list(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.query("Ravi", "default")
        assert isinstance(results, list)

    def test_finds_relevant_fact(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.query("Ravi", "default")
        assert len(results) > 0

    def test_returns_tuples(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.query("Ravi", "default")
        fact_text, score = results[0]
        assert isinstance(fact_text, str)
        assert isinstance(score, float)

    def test_empty_graph_returns_empty(self, kg: KnowledgeGraph) -> None:
        results = kg.query("anything", "default")
        assert results == []

    def test_no_match_returns_empty(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.query("xyz_no_match_abc", "default")
        assert results == []

    def test_top_k_respected(self, kg: KnowledgeGraph) -> None:
        facts = [make_fact("Ravi", f"action{i}", "Python") for i in range(10)]
        kg.add_facts(facts, "default")
        results = kg.query("Ravi", "default", top_k=3)
        assert len(results) <= 3

    def test_scores_between_zero_and_one(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.query("Ravi", "default")
        for _, score in results:
            assert 0.0 <= score <= 1.0


class TestGetEntityFacts:
    def test_finds_facts_for_entity(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.get_entity_facts("Ravi", "default")
        assert len(results) > 0

    def test_finds_as_object_too(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Alice", "knows", "Ravi")], "default")
        results = kg.get_entity_facts("Ravi", "default")
        assert len(results) > 0

    def test_unknown_entity_returns_empty(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")
        results = kg.get_entity_facts("nobody_xyz", "default")
        assert results == []


class TestDeleteSession:
    def test_delete_removes_graph(self, kg: KnowledgeGraph) -> None:
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "to-delete")
        assert kg.edge_count("to-delete") == 1
        kg.delete_session("to-delete")
        assert kg.edge_count("to-delete") == 0

    def test_delete_nonexistent_no_error(self, kg: KnowledgeGraph) -> None:
        kg.delete_session("does-not-exist")


class TestPersistence:
    def test_save_and_load(self, kg: KnowledgeGraph, tmp_path: "pytest.TempPathFactory") -> None:
        kg.add_entities([make_entity("Ravi", "PERSON")], "default")
        kg.add_facts([make_fact("Ravi", "likes", "Python")], "default")

        path = str(tmp_path / "graph.json")
        kg.save("default", path)

        # load into a fresh graph
        kg2 = KnowledgeGraph(MemoryConfig())
        kg2.load("default", path)

        assert kg2.node_count("default") > 0
        assert kg2.edge_count("default") == 1

    def test_load_nonexistent_raises(self, kg: KnowledgeGraph) -> None:
        with pytest.raises(GraphError):
            kg.load("default", "/nonexistent/path/graph.json")
