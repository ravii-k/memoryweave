# NLP pipeline — Phase 2 documentation

**Phase:** 2 of 8
**Branch:** phase/2-nlp
**Author:** Ravi Kashyap
**GitHub:** https://github.com/ravii-k
**Started:** 2026-03-29

---

## Overview

Phase 2 implements the NLP extraction pipeline — the first real stage of
the `memory.add()` pipeline. Raw text goes in, structured `EntityResult`
and `FactResult` objects come out.

Two sub-pipelines run in sequence (or together via `extract()`):

1. **Entity extraction** — finds named entities (people, orgs, locations, dates)
2. **Fact extraction** — pulls subject-predicate-object triples from sentences

---

## Chapter 2.1 — Entity extractor

**Status:** Complete
**Tests:** `tests/test_extractor.py` — 25 tests

### What was built

`memoryweave/extractor.py` — full implementation of:

| Class / Method | Purpose |
|---------------|---------|
| `EntityResult` | Dataclass for a single extracted entity |
| `FactResult` | Dataclass for a single SPO triple |
| `Extractor.__init__()` | Loads spaCy model once on init |
| `Extractor.extract_entities()` | Extracts named entities from raw text |
| `Extractor.extract_facts()` | Extracts SPO triples using dep parser |
| `Extractor.extract()` | Convenience method — runs both pipelines on one spaCy parse |
| `Extractor._extract_entities_from_doc()` | Entities from pre-parsed doc |
| `Extractor._extract_facts_from_doc()` | Facts from pre-parsed doc |
| `Extractor._get_span_text()` | Returns full noun phrase for a token |
| `Extractor._load_model()` | Loads spaCy with clear error if not installed |

### Entity labels extracted

Only labels that make useful memories are kept. Noise labels like
`CARDINAL`, `ORDINAL`, `MONEY`, `PERCENT`, `QUANTITY` are discarded.

| Label | Meaning |
|-------|---------|
| `PERSON` | People's names |
| `ORG` | Companies, organisations |
| `GPE` | Countries, cities, states |
| `LOC` | Non-GPE locations |
| `DATE` | Dates and periods |
| `TIME` | Times of day |
| `PRODUCT` | Products and software |
| `EVENT` | Named events |
| `WORK_OF_ART` | Titles of books, films, songs |
| `LAW` | Laws and legal documents |
| `LANGUAGE` | Named languages |
| `NORP` | Nationalities, religious/political groups |

### Fact extraction approach

Uses spaCy's dependency parser to find verb-rooted clauses:

1. Find the `ROOT` verb of each sentence
2. Find `nsubj` or `nsubjpass` children → subject
3. Find `dobj`, `attr`, `pobj`, `acomp` children → object
4. Check `prep` children for prepositional objects ("works **at** Google")
5. Use noun chunk spans instead of head tokens for full names

Predicates are lemmatised (lowercase) — "works" → "work", "likes" → "like".

### Design decisions

**Why spaCy over transformers?**
spaCy runs fully offline with no API key, loads in ~200ms, and processes
text fast enough for interactive use. Transformer-based NER is more accurate
but 10x slower and requires network access. For a memory SDK that runs in
every `add()` call, speed matters more than marginal accuracy gains.
*Decision by: Ravi Kashyap · 2026-03-29*

**Why `en_core_web_sm` as default?**
80MB model, fast on CPU, good enough for common entity types. Users who
need better accuracy can swap to `en_core_web_lg` in `MemoryConfig`.
*Decision by: Ravi Kashyap · 2026-03-29*

**Why deduplication by (text, label)?**
The same entity mentioned twice in a message shouldn't create two nodes
in the knowledge graph. We deduplicate at extraction time rather than
graph insertion time to keep the graph layer simple.
*Decision by: Ravi Kashyap · 2026-03-29*

**Why confidence 0.8 for facts?**
Dependency parsing is imperfect. Setting confidence to 0.8 instead of 1.0
signals to the ranker that facts carry slightly less certainty than direct
entity mentions. Will tune this value after Phase 4 benchmarks.
*Decision by: Ravi Kashyap · 2026-03-29*

**Why parse once in extract()?**
`memory.add()` needs both entities and facts. Calling `extract_entities()`
then `extract_facts()` would run spaCy twice on the same text. The `extract()`
convenience method runs the parser once and passes the `Doc` to both
internal methods — roughly 2x faster for the common case.
*Decision by: Ravi Kashyap · 2026-03-29*

---

## Chapter 2.2 — Pipeline tests and confidence scoring

**Status:** Complete
**Tests:** `tests/test_extractor_pipeline.py` — 18 tests

### What was built

- `extract()` convenience method — single spaCy parse for both pipelines
- `_extract_entities_from_doc()` and `_extract_facts_from_doc()` private methods
- Full pipeline test suite covering:
  - Return types and structure
  - Confidence score ranges
  - Edge cases (unicode, caps, long text, questions, punctuation-only)
  - Performance bounds (short text < 1s, paragraph < 3s)

---

## Chapter 2.3 — Accuracy benchmarks

**Status:** Complete
**Tests:** `tests/test_extractor_accuracy.py` — 18 tests

### Benchmark results (en_core_web_sm, Python 3.14, M2 MacBook Air)

| Metric | Result |
|--------|--------|
| Person recall (3 sentences) | ≥ 2/3 |
| Org recall (3 sentences) | ≥ 2/3 |
| Location recall (3 sentences) | ≥ 2/3 |
| False positives on plain text | ≤ 2 across 3 sentences |
| Multi-entity sentence | ≥ 2 distinct types |
| Common fact patterns | works_at, likes, lives_in, founded |

### Known limitations

- `en_core_web_sm` struggles with ambiguous short names ("Ravi" sometimes
  tagged as `ORG` in certain sentence contexts)
- Dependency-based fact extraction misses complex sentence structures
  (passive voice, subordinate clauses, coordinated predicates)
- No temporal fact extraction yet — "Ravi has worked at Google since 2020"
  loses the "since 2020" part (planned for Phase 6)
- No coreference resolution — "Ravi works at Google. He likes Python."
  extracts two separate subjects rather than linking "He" → "Ravi"

---

## Dependencies introduced this phase

| Package | Version | Purpose |
|---------|---------|---------|
| `spacy` | >=3.7 | NLP pipeline — entity and dependency parsing |
| `en_core_web_sm` | latest | spaCy English model (downloaded separately) |

Install:
```bash
pip install memoryweave[nlp]
python -m spacy download en_core_web_sm
```

---

## Test coverage after Phase 2

| Module | Coverage |
|--------|---------|
| `extractor.py` | 90% |
| `errors.py` | 100% |
| `config.py` | 100% |
| `client.py` | 100% |
| **Total** | **~69%** |

---

## What Phase 3 builds on top of

Phase 3 (storage layer) will import `EntityResult` and `FactResult` from
this module and store them in:

1. **Vector store** — embeds the raw text via sentence-transformers
2. **Knowledge graph** — stores entities as nodes, facts as edges

The `Extractor` will be instantiated once in the `MemoryWeave` client and
called on every `memory.add()` invocation.

---

*Document created: Ravi Kashyap 2026-03-29 (Phase 2, Chapter 2.3)*
