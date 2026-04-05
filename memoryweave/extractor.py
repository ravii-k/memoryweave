"""NLP extraction pipeline — pulls entities and facts out of raw text.

This is the first stage of the memory.add() pipeline. Raw text goes in,
structured EntityResult and FactResult objects come out.

Using spaCy as the primary extractor — fast, well-tested, runs offline.
en_core_web_sm is the default model. Users can swap to en_core_web_lg
in MemoryConfig if they need better accuracy at the cost of more RAM.
"""

from __future__ import annotations

import spacy
from spacy.language import Language

from memoryweave.config import MemoryConfig
from memoryweave.errors import ExtractionError
from memoryweave.logger import get_logger

logger = get_logger(__name__)

# spaCy entity labels we care about — ignoring things like CARDINAL,
# ORDINAL, QUANTITY that rarely make useful memories
_USEFUL_LABELS = {
    "PERSON",
    "ORG",
    "GPE",  # countries, cities, states
    "LOC",  # non-GPE locations
    "DATE",
    "TIME",
    "PRODUCT",
    "EVENT",
    "WORK_OF_ART",
    "LAW",
    "LANGUAGE",
    "NORP",  # nationalities, religious groups, political groups
}


class EntityResult:
    """A single entity extracted from text.

    Attributes
    ----------
        text: The entity as it appears in the source text (e.g. "Ravi Kashyap").
        label: Entity type — PERSON, ORG, DATE, GPE, etc.
        confidence: How confident the model is. spaCy doesn't give this
            directly so we default to 1.0 for matched entities.
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EntityResult):
            return NotImplemented
        return self.text == other.text and self.label == other.label


class FactResult:
    """A single fact as a subject-predicate-object triple.

    Keeping it simple with SPO triples for now. Might move to a more
    expressive representation later if the graph queries need it.

    Attributes
    ----------
        subject: Who or what the fact is about (e.g. "Ravi").
        predicate: The relationship (e.g. "prefers", "works at").
        obj: The object of the fact (e.g. "Python", "Anthropic").
        confidence: Extraction confidence score (0.0-1.0).
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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FactResult):
            return NotImplemented
        return (
            self.subject == other.subject
            and self.predicate == other.predicate
            and self.obj == other.obj
        )


class Extractor:
    """NLP pipeline for extracting entities and facts from raw text.

    Loads a spaCy model once on init — we pay that startup cost one time
    so repeated add() calls stay fast. The model is not thread-safe so
    each client instance should have its own Extractor.

    Args:
    ----
        config: Controls which spaCy model to load and other NLP settings.

    """

    def __init__(self, config: MemoryConfig) -> None:
        self.config = config
        self._nlp: Language = self._load_model(config.spacy_model)

    def _load_model(self, model_name: str) -> Language:
        """Load the spaCy model, with a clear error if it's not installed."""
        try:
            nlp = spacy.load(model_name)
            logger.debug("loaded spaCy model %r", model_name)
            return nlp
        except OSError as e:
            raise ExtractionError(
                f"spaCy model {model_name!r} not found. "
                f"Install it with: python -m spacy download {model_name}"
            ) from e

    def extract_entities(self, text: str) -> list[EntityResult]:
        """Pull named entities out of raw text using spaCy.

        Filters to only useful entity types — ignores CARDINAL, ORDINAL,
        MONEY etc. that rarely make meaningful memories. Deduplicates
        by (text, label) so the same entity mentioned twice only appears once.

        Args:
        ----
            text: Raw input text to process. Can be a sentence, paragraph,
                or full document.

        Returns:
        -------
            List of EntityResult objects, deduplicated, sorted by position.
            Empty list if no useful entities found.

        Raises:
        ------
            ExtractionError: If text is empty or the model fails.

        """
        if not text or not text.strip():
            raise ExtractionError("cannot extract entities from empty text")

        logger.debug("extracting entities from %d chars", len(text))

        try:
            doc = self._nlp(text)
        except Exception as e:
            raise ExtractionError(f"spaCy processing failed: {e}") from e

        return self._extract_entities_from_doc(doc)

    def extract_facts(self, text: str) -> list[FactResult]:
        """Extract subject-predicate-object triples from raw text.

        Uses spaCy's dependency parser to find verb-rooted clauses and
        pull out the subject, verb, and object. Works well for simple
        declarative sentences like "Ravi works at Anthropic" or
        "I prefer Python over JavaScript".

        Not perfect — dependency parsing is hard and we'll miss some facts.
        Good enough for the memory use case where recall matters more
        than precision. Will improve this in future phases.

        Args:
        ----
            text: Raw input text to process.

        Returns:
        -------
            List of FactResult triples. Empty list if none found.

        Raises:
        ------
            ExtractionError: If text is empty or the model fails.

        """
        if not text or not text.strip():
            raise ExtractionError("cannot extract facts from empty text")

        logger.debug("extracting facts from %d chars", len(text))

        try:
            doc = self._nlp(text)
        except Exception as e:
            raise ExtractionError(f"spaCy processing failed: {e}") from e

        return self._extract_facts_from_doc(doc)

    def extract(self, text: str) -> tuple[list[EntityResult], list[FactResult]]:
        """Run both entity and fact extraction in one call.

        Convenience method — runs spaCy once and reuses the doc for both
        pipelines instead of parsing the same text twice.

        Args:
        ----
            text: Raw input text to process.

        Returns:
        -------
            Tuple of (entities, facts).

        Raises:
        ------
            ExtractionError: If text is empty or the model fails.

        """
        if not text or not text.strip():
            raise ExtractionError("cannot extract from empty text")

        logger.debug("running full extraction pipeline on %d chars", len(text))

        try:
            doc = self._nlp(text)
        except Exception as e:
            raise ExtractionError(f"spaCy processing failed: {e}") from e

        entities = self._extract_entities_from_doc(doc)
        facts = self._extract_facts_from_doc(doc)

        logger.debug(
            "extraction complete — %d entities, %d facts",
            len(entities),
            len(facts),
        )
        return entities, facts

    def _extract_entities_from_doc(self, doc: spacy.tokens.Doc) -> list[EntityResult]:
        """Extract entities from an already-parsed spaCy doc."""
        seen: set[tuple[str, str]] = set()
        results: list[EntityResult] = []

        for ent in doc.ents:
            if ent.label_ not in _USEFUL_LABELS:
                continue
            key = (ent.text.strip(), ent.label_)
            if key in seen:
                continue
            seen.add(key)
            results.append(
                EntityResult(
                    text=ent.text.strip(),
                    label=ent.label_,
                    confidence=1.0,
                    start=ent.start_char,
                    end=ent.end_char,
                )
            )
        return results

    def _extract_facts_from_doc(self, doc: spacy.tokens.Doc) -> list[FactResult]:
        """Extract SPO fact triples from an already-parsed spaCy doc."""
        results: list[FactResult] = []

        for sent in doc.sents:
            root = next((token for token in sent if token.dep_ == "ROOT"), None)
            if root is None or root.pos_ not in ("VERB", "AUX"):
                continue

            subjects = [t for t in root.children if t.dep_ in ("nsubj", "nsubjpass")]
            objects = [t for t in root.children if t.dep_ in ("dobj", "attr", "pobj", "acomp")]

            for prep in root.children:
                if prep.dep_ == "prep":
                    for pobj in prep.children:
                        if pobj.dep_ == "pobj":
                            objects.append(pobj)

            if not subjects or not objects:
                continue

            subj_text = self._get_span_text(subjects[0])
            obj_text = self._get_span_text(objects[0])
            pred_text = root.lemma_.lower()

            if not subj_text or not obj_text:
                continue

            results.append(
                FactResult(
                    subject=subj_text,
                    predicate=pred_text,
                    obj=obj_text,
                    confidence=0.8,
                )
            )
        return results

    def _get_span_text(self, token: spacy.tokens.Token) -> str:
        """Get the full noun phrase text for a token.

        Instead of just returning "Ravi" we want "Ravi Kashyap",
        instead of "Python" we want "Python" but instead of "developer"
        we might want "senior developer".
        """
        # walk up to find if this token is part of a noun chunk
        for chunk in token.doc.noun_chunks:
            if token in chunk:
                return chunk.text.strip()
        return token.text.strip()
