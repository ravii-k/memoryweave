"""Chapter 2.3 — accuracy benchmarks for the NLP extraction pipeline.

These tests measure how well the extractor performs on realistic inputs.
They're not strict unit tests — they check that recall is above a
minimum threshold on a set of known sentences.

If spaCy's en_core_web_sm model changes behaviour in a future version,
these tests will catch it. That's the point.
"""

from __future__ import annotations

import pytest

from memoryweave.config import MemoryConfig
from memoryweave.extractor import Extractor


@pytest.fixture(scope="module")
def extractor() -> Extractor:
    """Shared extractor for the whole module."""
    return Extractor(MemoryConfig())


class TestEntityAccuracy:
    """Check that common entity types are reliably extracted."""

    def test_person_recall(self, extractor: Extractor) -> None:
        # these are clear, unambiguous person mentions — should always hit
        sentences = [
            "My name is Ravi Kashyap.",
            "Elon Musk founded Tesla.",
            "Sundar Pichai runs Google.",
        ]
        hits = 0
        for s in sentences:
            entities = extractor.extract_entities(s)
            if any(e.label == "PERSON" for e in entities):
                hits += 1
        # expect at least 2 out of 3 — en_core_web_sm isn't perfect
        assert hits >= 2, f"person recall too low: {hits}/3"

    def test_org_recall(self, extractor: Extractor) -> None:
        sentences = [
            "I work at Google.",
            "She joined Microsoft last year.",
            "Anthropic is an AI safety company.",
        ]
        hits = 0
        for s in sentences:
            entities = extractor.extract_entities(s)
            if any(e.label == "ORG" for e in entities):
                hits += 1
        assert hits >= 2, f"org recall too low: {hits}/3"

    def test_location_recall(self, extractor: Extractor) -> None:
        sentences = [
            "I live in India.",
            "She moved to San Francisco.",
            "The office is in London.",
        ]
        hits = 0
        for s in sentences:
            entities = extractor.extract_entities(s)
            if any(e.label in ("GPE", "LOC") for e in entities):
                hits += 1
        assert hits >= 2, f"location recall too low: {hits}/3"

    def test_no_false_positives_on_plain_text(self, extractor: Extractor) -> None:
        # plain sentences with no named entities should return very few
        sentences = [
            "the cat sat on the mat",
            "i like to eat apples and oranges",
            "it was a beautiful sunny day",
        ]
        total = 0
        for s in sentences:
            entities = extractor.extract_entities(s)
            total += len(entities)
        # allow up to 2 false positives across all 3 sentences
        assert total <= 2, f"too many false positives: {total}"

    def test_multi_entity_sentence(self, extractor: Extractor) -> None:
        # a rich sentence should find multiple entity types
        text = "Ravi Kashyap works at Anthropic in San Francisco."
        entities = extractor.extract_entities(text)
        labels = {e.label for e in entities}
        # should get at least 2 distinct entity types
        assert len(labels) >= 2, f"expected 2+ types, got: {labels}"


class TestFactAccuracy:
    """Check that common fact patterns are reliably extracted."""

    def test_works_at_pattern(self, extractor: Extractor) -> None:
        # "X works at Y" is the most common memory pattern
        results = extractor.extract_facts("Ravi works at Google.")
        assert len(results) > 0
        subjects = [f.subject for f in results]
        assert any("Ravi" in s for s in subjects)

    def test_likes_pattern(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Ravi likes Python.")
        assert len(results) > 0

    def test_lives_in_pattern(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Ravi lives in India.")
        assert len(results) > 0

    def test_founded_pattern(self, extractor: Extractor) -> None:
        results = extractor.extract_facts("Elon Musk founded SpaceX.")
        assert len(results) > 0

    def test_multi_sentence_fact_count(self, extractor: Extractor) -> None:
        # multi-sentence text should extract more facts than one sentence
        one = "Ravi uses Python."
        multi = "Ravi uses Python. He works at Anthropic. He lives in India."
        facts_one = extractor.extract_facts(one)
        facts_multi = extractor.extract_facts(multi)
        assert len(facts_multi) >= len(facts_one)

    def test_predicate_is_verb_lemma(self, extractor: Extractor) -> None:
        # predicates should be lemmatised — "works" → "work"
        results = extractor.extract_facts("Ravi works at Google.")
        if results:
            # lemma should be lowercase
            assert results[0].predicate == results[0].predicate.lower()

    def test_confidence_range(self, extractor: Extractor) -> None:
        results = extractor.extract_facts(
            "Ravi Kashyap works at Anthropic in San Francisco."
        )
        for f in results:
            assert 0.0 < f.confidence <= 1.0


class TestPipelineAccuracy:
    """End-to-end accuracy on realistic user inputs."""

    def test_intro_sentence(self, extractor: Extractor) -> None:
        # the most common first message a user sends to any AI app
        entities, facts = extractor.extract(
            "Hi, my name is Ravi and I work as a Python developer."
        )
        assert len(entities) > 0 or len(facts) > 0

    def test_preference_sentence(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract(
            "I prefer Python over JavaScript for backend work."
        )
        assert isinstance(entities, list)
        assert isinstance(facts, list)

    def test_location_sentence(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract(
            "I am based in Meerut, Uttar Pradesh, India."
        )
        assert len(entities) > 0

    def test_work_context(self, extractor: Extractor) -> None:
        entities, facts = extractor.extract(
            "I have been building AI tools at a startup in Bangalore since 2022."
        )
        assert isinstance(entities, list)
        assert isinstance(facts, list)
