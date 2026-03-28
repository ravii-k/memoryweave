"""NLP extraction pipeline — pulls entities and facts out of raw text.

This is the first stage of the memory.add() pipeline. Raw text goes in,
structured EntityResult and FactResult objects come out.

Went with spaCy as the primary extractor because it's fast, well-tested,
and runs offline. GLiNER is a good fallback for custom entity types that
spaCy's pretrained models miss — will wire that up in Phase 2.
"""

from __future__ import annotations

# will be uncommented in Phase 2, Chapter 2.1
# import spacy
# from gliner import GLiNER
from memoryweave.config import MemoryConfig


class EntityResult:
    """A single entity extracted from text.

    Attributes:
        text: The entity as it appears in the source text (e.g. "Ravi Kashyap").
        label: Entity type — PERSON, ORG, DATE, GPE, etc.
        confidence: How confident the model is. spaCy doesn't give this
            directly so we default to 1.0 and adjust in GLiNER fallback.
        start: Character offset where the entity starts in the source text.
        end: Character offset where it ends.
    """

    def __init__(
        self,
        text: str,
        label: str,
        confidence: float = 1.0,
        start: int = 0,
        end: int = 0,
    ) -> None:
        self.text = text
        self.label = label
        self.confidence = confidence
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        return f"EntityResult(text={self.text!r}, label={self.label!r})"


class FactResult:
    """A single fact as a subject-predicate-object triple.

    Keeping it simple with SPO triples for now. Might move to a more
    expressive representation later if the graph queries need it.

    Attributes:
        subject: Who or what the fact is about (e.g. "Ravi").
        predicate: The relationship (e.g. "prefers", "works at").
        obj: The object of the fact (e.g. "Python", "Anthropic").
        confidence: Extraction confidence score (0.0–1.0).
        temporal: Time reference if there is one (e.g. "since 2022").
            Empty string if the fact has no temporal component.
    """

    def __init__(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        temporal: str = "",
    ) -> None:
        self.subject = subject
        self.predicate = predicate
        self.obj = obj
        self.confidence = confidence
        self.temporal = temporal

    def __repr__(self) -> str:
        return f"FactResult({self.subject!r} {self.predicate!r} {self.obj!r})"


class Extractor:
    """Runs entity and fact extraction on raw text.

    Two sub-pipelines:
    1. Entity extraction — spaCy + GLiNER fallback for custom types
    2. Fact extraction — subject-predicate-object triples

    Both get implemented in Phase 2. The dataclasses above are ready
    so Phase 3 and 4 can reference them without waiting.

    Args:
        config: Controls which spaCy model to load.
    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        # loading the spaCy model on init so we pay the cost once,
        # not on every add() call — will uncomment in Phase 2
        # self._nlp = spacy.load(config.spacy_model)

    def extract_entities(self, text: str) -> list[EntityResult]:
        """Pull named entities out of raw text.

        Args:
            text: Raw input text to process.

        Returns:
            List of EntityResult objects. Empty list if none found.

        Raises:
            ExtractionError: If the model fails or text is empty.
        """
        # Phase 2, Chapter 2.1
        raise NotImplementedError("coming in Phase 2, Chapter 2.1")

    def extract_facts(self, text: str) -> list[FactResult]:
        """Pull subject-predicate-object triples out of raw text.

        Args:
            text: Raw input text to process.

        Returns:
            List of FactResult objects. Empty list if none found.

        Raises:
            ExtractionError: If the model fails or text is empty.
        """
        # Phase 2, Chapter 2.2
        raise NotImplementedError("coming in Phase 2, Chapter 2.2")
