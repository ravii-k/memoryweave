"""NLP extraction pipeline — entity and fact extraction from raw text.

Takes raw text and returns structured EntityResult and FactResult objects.
This module is the first stage of the memory.add() pipeline.

Full implementation: Phase 2, Chapters 2.1 and 2.2.

Author: Ravi Kashyap
Created: 2026-03-23 (Phase 1, Chapter 1.2)
"""

from __future__ import annotations

# TODO [Ravi Kashyap] 2026-03-23 - Uncomment in Phase 2, Chapter 2.1.
# import spacy
# from gliner import GLiNER

from memoryweave.config import MemoryConfig


class EntityResult:
    """Represents a single extracted entity from text.

    Attributes:
        text: The entity surface form (e.g. "Ravi Kashyap").
        label: Entity type (e.g. "PERSON", "ORG", "DATE", "GPE").
        confidence: Extraction confidence score (0.0–1.0).
        start: Character offset start in the source text.
        end: Character offset end in the source text.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(
        self,
        text: str,
        label: str,
        confidence: float = 1.0,
        start: int = 0,
        end: int = 0,
    ) -> None:
        """Initialise an EntityResult.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.text = text
        self.label = label
        self.confidence = confidence
        self.start = start
        self.end = end

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        return f"EntityResult(text={self.text!r}, label={self.label!r})"


class FactResult:
    """Represents a single extracted fact (subject-predicate-object triple).

    Attributes:
        subject: The entity the fact is about (e.g. "Ravi").
        predicate: The relationship (e.g. "prefers").
        obj: The object of the fact (e.g. "Python").
        confidence: Extraction confidence score (0.0–1.0).
        temporal: Optional time reference (e.g. "since 2020").

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(
        self,
        subject: str,
        predicate: str,
        obj: str,
        confidence: float = 1.0,
        temporal: str = "",
    ) -> None:
        """Initialise a FactResult.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.subject = subject
        self.predicate = predicate
        self.obj = obj
        self.confidence = confidence
        self.temporal = temporal

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        return (
            f"FactResult({self.subject!r} {self.predicate!r} {self.obj!r})"
        )


class Extractor:
    """NLP pipeline for extracting entities and facts from raw text.

    Runs two sub-pipelines:
    1. Entity extraction (spaCy + GLiNER fallback)
    2. Fact extraction (subject-predicate-object triples)

    Full implementation: Phase 2, Chapters 2.1 and 2.2.

    Args:
        config: MemoryConfig instance controlling the spaCy model used.

    Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
    """

    def __init__(self, config: MemoryConfig) -> None:
        """Initialise the Extractor.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        self.config = config
        # TODO [Ravi Kashyap] 2026-03-23 - Load spaCy model here in Phase 2.
        # self._nlp = spacy.load(config.spacy_model)

    def extract_entities(self, text: str) -> list[EntityResult]:
        """Extract named entities from raw text.

        Args:
            text: Raw input text to process.

        Returns:
            List of EntityResult objects, one per detected entity.

        Raises:
            ExtractionError: If the NLP model fails to process the text.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 2, Chapter 2.1.
        raise NotImplementedError(
            "extract_entities() will be implemented in Phase 2, Chapter 2.1."
        )

    def extract_facts(self, text: str) -> list[FactResult]:
        """Extract subject-predicate-object fact triples from raw text.

        Args:
            text: Raw input text to process.

        Returns:
            List of FactResult objects, one per detected fact.

        Raises:
            ExtractionError: If the NLP model fails to process the text.

        Added: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)
        """
        # TODO [Ravi Kashyap] 2026-03-23 - Implement in Phase 2, Chapter 2.2.
        raise NotImplementedError(
            "extract_facts() will be implemented in Phase 2, Chapter 2.2."
        )
