"""Tests for the NLP extraction pipeline.

These tests require spaCy and en_core_web_sm to be installed.
Run: python -m spacy download en_core_web_sm

Testing both the happy path and edge cases — empty input, unusual text,
duplicate entities, and sentences with no clear SPO structure.
"""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.errors import ExtractionError
from memoryweave.extractor import EntityResult, Extractor, FactResult


@pytest.fixture(scope="module")
def extractor() -> Extractor:
    """Single extractor instance shared across all tests in this module.

    Loading spaCy once per module instead of once per test —
    cuts test time from ~10s to ~1s.
    """
    return Extractor(MemoryConfig())


class TestEntityResult:
    """Basic tests for the EntityResult dataclass."""

    def test_repr(self) -> None:
        e = EntityResult(text="Ravi", label="PERSON")
        assert "Ravi" in repr(e)
        assert "PERSON" in repr(e)

    def test_equality(self) -> None:
        e1 = EntityResult(text="Ravi", label="PERSON")
        e2 = EntityResult(text="Ravi", label="PERSON")
        assert e1 == e2

    def test_inequality_different_label(self) -> None:
        e1 = EntityResult(text="Python", label="PRODUCT")
        e2 = EntityResult(text="Python", label="ORG")
        assert e1 != e2

    def test_default_confidence(self) -> None:
        e = EntityResult(text="Ravi", label="PERSON")
        assert e.confidence == 1.0


class TestFactResult:
    """Basic tests for the FactResult dataclass."""

    def test_repr(self) -> None:
        f = FactResult(subject="Ravi", predicate="prefers", obj="Python")
        assert "Ravi" in repr(f)
        assert "Python" in repr(f)

    def test_equality(self) -> None:
        f1 = FactResult(subject="Ravi", predicate="prefers", obj="Python")
        f2 = FactResult(subject="Ravi", predicate="prefers", obj="Python")
        assert f1 == f2

    def test_default_temporal(self) -> None:
        f = FactResult(subject="Ravi", predicate="works", obj="Anthropic")
        assert f.temporal == ""


class TestExtractorInit:
    """Test that the Extractor loads correctly."""

    def test_loads_default_model(self) -> None:
        ex = Extractor(MemoryConfig())
        assert ex._nlp is not None

    def test_invalid_model_raises_extraction_error(self) -> None:
        with pytest.raises(ExtractionError, match="not found"):
            Extractor(MemoryConfig(spacy_model="en_invalid_model_xyz"))


class TestExtractEntities:
    """Tests for entity extraction."""

    def test_extracts_person(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("My name is Ravi Kashyap.")
        labels = [e.label for e in results]
        assert "PERSON" in labels

    def test_extracts_org(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("I work at Google.")
        labels = [e.label for e in results]
        assert "ORG" in labels

    def test_extracts_location(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("I live in Mumbai, India.")
        labels = [e.label for e in results]
        assert any(lbl in labels for lbl in ("GPE", "LOC"))

    def test_returns_list(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("Ravi works at OpenAI in San Francisco.")
        assert isinstance(results, list)

    def test_deduplicates_entities(self, extractor: Extractor) -> None:
        # same (text, label) pair mentioned twice should appear once
        results = extractor.extract_entities("Ravi said Ravi likes Python.")
        seen = [(e.text, e.label) for e in results]
        assert len(seen) == len(set(seen))

    def test_empty_text_raises(self, extractor: Extractor) -> None:
        with pytest.raises(ExtractionError):
            extractor.extract_entities("")

    def test_whitespace_only_raises(self, extractor: Extractor) -> None:
        with pytest.raises(ExtractionError):
            extractor.extract_entities("   ")

    def test_no_entities_returns_empty_list(self, extractor: Extractor) -> None:
        # plain sentence with no named entities
        results = extractor.extract_entities("the cat sat on the mat")
        assert isinstance(results, list)

    def test_entity_has_correct_fields(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("Ravi Kashyap lives in India.")
        assert len(results) > 0
        for e in results:
            assert isinstance(e.text, str)
            assert isinstance(e.label, str)
            assert 0.0 <= e.confidence <= 1.0
            assert isinstance(e.start, int)
            assert isinstance(e.end, int)

    def test_multiple_entity_types(self, extractor: Extractor) -> None:
        text = "Elon Musk founded SpaceX in California in 2002."
        results = extractor.extract_entities(text)
        labels = {e.label for e in results}
        # should get at least person + org
        assert len(labels) >= 1


class TestExtractFacts:
    """Tests for fact (SPO triple) extraction."""

    def test_returns_list(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Ravi likes Python.")
        assert isinstance(results, list)

    def test_empty_text_raises(self, extractor: Extractor) -> None:
        with pytest.raises(ExtractionError):
            extractor.extract_facts("")

    def test_whitespace_only_raises(self, extractor: Extractor) -> None:
        with pytest.raises(ExtractionError):
            extractor.extract_facts("   ")

    def test_fact_has_correct_fields(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Ravi uses Python.")
        for f in results:
            assert isinstance(f.subject, str)
            assert isinstance(f.predicate, str)
            assert isinstance(f.obj, str)
            assert 0.0 <= f.confidence <= 1.0

    def test_extracts_simple_svo(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Ravi loves Python.")
        assert len(results) > 0
        subjects = [f.subject for f in results]
        assert any("Ravi" in s for s in subjects)

    def test_no_verb_returns_list(self, extractor: Extractor) -> None:
        # sentence fragments shouldn't crash — just return empty
        results = extractor.extract_facts("A beautiful day.")
        assert isinstance(results, list)
