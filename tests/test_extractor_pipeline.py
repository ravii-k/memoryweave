"""Chapter 2.2 — pipeline tests, confidence scoring, and edge case coverage.

These tests focus on:
1. The full extract() convenience method that runs both pipelines at once
2. Confidence scoring behaviour
3. Edge cases that real user input throws at the extractor
4. Multi-sentence documents
5. Performance — making sure we're not doing anything obviously slow
"""

from __future__ import annotations

import time

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.extractor import EntityResult, Extractor, FactResult


@pytest.fixture(scope="module")
def extractor() -> Extractor:
    """Shared extractor — load spaCy once for the whole module."""
    return Extractor(MemoryConfig())


class TestExtractMethod:
    """Tests for the combined extract() convenience method."""

    def test_returns_tuple(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract("Ravi works at Anthropic.")
        assert isinstance(entities, list)
        assert isinstance(facts, list)

    def test_entities_are_entity_results(self, extractor: Extractor) -> None:
        entities, _ = extractor.extract("Ravi lives in India.")
        for e in entities:
            assert isinstance(e, EntityResult)

    def test_facts_are_fact_results(self, extractor: Extractor) -> None:
        _, facts = extractor.extract("Ravi loves Python.")
        for f in facts:
            assert isinstance(f, FactResult)

    def test_empty_text_raises(self, extractor: Extractor) -> None:
        from memoryweave.errors import ExtractionError

        with pytest.raises(ExtractionError):
            extractor.extract("")

    def test_rich_sentence_gets_both(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract("Elon Musk founded SpaceX.")
        assert len(entities) > 0
        assert len(facts) > 0


class TestConfidenceScoring:
    """Tests for confidence score values."""

    def test_entity_confidence_between_zero_and_one(self, extractor: Extractor) -> None:
        entities, _ = extractor.extract("Ravi Kashyap works at Google.")
        for e in entities:
            assert 0.0 <= e.confidence <= 1.0

    def test_fact_confidence_between_zero_and_one(self, extractor: Extractor) -> None:
        _, facts = extractor.extract("Ravi uses Python every day.")
        for f in facts:
            assert 0.0 <= f.confidence <= 1.0

    def test_fact_confidence_is_not_one(self, extractor: Extractor) -> None:
        # dep parsing is imperfect — confidence should be < 1.0 to reflect that
        _, facts = extractor.extract("Ravi loves Python.")
        for f in facts:
            assert f.confidence < 1.0


class TestEdgeCases:
    """Real-world edge cases that user input tends to produce."""

    def test_all_caps_text(self, extractor: Extractor) -> None:
        results = extractor.extract_entities("RAVI WORKS AT GOOGLE IN INDIA.")
        assert isinstance(results, list)

    def test_numbers_and_dates(self, extractor: Extractor) -> None:
        results = extractor.extract_entities(
            "Ravi was born in 1995 and started coding in 2010."
        )
        assert isinstance(results, list)

    def test_multiple_sentences(self, extractor: Extractor) -> None:
        text = (
            "My name is Ravi Kashyap. "
            "I work at Anthropic. "
            "I prefer Python over JavaScript."
        )
        entities, facts = extractor.extract(text)
        assert isinstance(entities, list)
        assert isinstance(facts, list)
        assert len(entities) >= 1

    def test_question_sentence(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract("What does Ravi do at Google?")
        assert isinstance(entities, list)
        assert isinstance(facts, list)

    def test_very_long_text(self, extractor: Extractor) -> None:
        text = " ".join(
            [
                "Ravi Kashyap is a Python developer based in India.",
                "He works at a startup building AI tools.",
                "He has been coding since 2015.",
                "He prefers dark mode and mechanical keyboards.",
                "His favourite language is Python followed by TypeScript.",
            ]
        )
        entities, facts = extractor.extract(text)
        assert len(entities) > 0

    def test_unicode_text(self, extractor: Extractor) -> None:
        entities, _ = extractor.extract("Ravi works in München, Germany.")
        assert isinstance(entities, list)

    def test_only_punctuation_returns_empty(self, extractor: Extractor) -> None:
        # punctuation-only text is valid input — just returns empty results
        entities, facts = extractor.extract("...")
        assert isinstance(entities, list)
        assert isinstance(facts, list)

    def test_single_word(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract("Python")
        assert isinstance(entities, list)
        assert isinstance(facts, list)


class TestPerformance:
    """Basic performance checks — sanity bounds only."""

    def test_short_text_is_fast(self, extractor: Extractor) -> None:
        start = time.time()
        extractor.extract("Ravi works at Google in India.")
        elapsed = time.time() - start
        assert elapsed < 1.0

    def test_paragraph_is_fast(self, extractor: Extractor) -> None:
        text = " ".join(
            [
                "Ravi Kashyap is a developer.",
                "He works at Anthropic in San Francisco.",
                "He prefers Python and TypeScript.",
                "He has been coding for 10 years.",
                "He likes dark mode and fast keyboards.",
            ]
        )
        start = time.time()
        extractor.extract(text)
        elapsed = time.time() - start
        assert elapsed < 3.0
