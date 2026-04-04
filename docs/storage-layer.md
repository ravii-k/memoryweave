# Storage layer — Phase 3 documentation

**Phase:** 3 of 8
**Branch:** phase/3-storage
**Author:** Ravi Kashyap
**GitHub:** https://github.com/ravii-k
**Started:** 2026-03-31

---

## Overview

Phase 3 implements the two storage systems that sit at the heart of MemoryWeave:

1. **Vector store** — semantic search over memory embeddings
2. **Knowledge graph** — structured entity and relationship queries

Both run independently but are queried together by the ranker (Phase 4)
to produce the final `MemoryContext` result.

---

## Chapter 3.1 — Vector embedder

**Status:** Complete
**Tests:** `tests/test_embedder.py` — 24 tests

### What was built

`memoryweave/embedder.py`:

| Method | Purpose |
|--------|---------|
| `Embedder.__init__()` | Loads sentence-transformers model once on init |
| `Embedder.embed()` | Embeds a single text string → 384-dim vector |
| `Embedder.embed_batch()` | Embeds a list of texts in one pass (faster) |
| `Embedder.similarity()` | Cosine similarity between two vectors |
| `Embedder.dimension` | Returns the embedding dimension (384 for default) |

### Design decisions

**Why sentence-transformers?**
Runs fully offline, no API key, no cost per embedding. The default
`all-MiniLM-L6-v2` model is 80MB and runs on CPU — fast enough for
interactive use in every `memory.add()` call.
*Decision by: Ravi Kashyap · 2026-03-31*

**Why 384 dimensions?**
`all-MiniLM-L6-v2` produces 384-dim vectors. This is a good balance
between quality and storage/search speed. Larger models (768-dim) are
more accurate but slower and larger. Can be swapped via `MemoryConfig`.
*Decision by: Ravi Kashyap · 2026-03-31*

---

## Chapter 3.2 — Vector store

**Status:** Complete
**Tests:** `tests/test_store.py` — 32 tests

### What was built

`memoryweave/store.py`:

| Class | Purpose |
|-------|---------|
| `MemoryItem` | Single stored memory — text + embedding + metadata |
| `BaseStore` | Abstract interface + factory method |
| `InMemoryStore` | In-process store, zero setup, no persistence |
| `ChromaStore` | ChromaDB-backed, local persistence, ANN search |

### Design decisions

**Why two backends?**
`InMemoryStore` is the default — zero setup, great for development and
testing. `ChromaStore` is for production use where you need data to
survive restarts. Swapping between them is one config line.
*Decision by: Ravi Kashyap · 2026-04-01*

**Why per-session ChromaDB collections?**
Each session gets its own ChromaDB collection. This gives strong
isolation between users — no cross-session leakage is possible at the
storage level, regardless of how the application layer behaves.
*Decision by: Ravi Kashyap · 2026-04-01*

**Why cosine similarity for InMemoryStore?**
Cosine similarity measures the angle between vectors regardless of
magnitude — it's the right metric for semantic similarity. Two texts
that mean the same thing will have similar angles even if their raw
embeddings have different magnitudes.
*Decision by: Ravi Kashyap · 2026-04-01*

### Install

```bash
pip install chromadb  # only needed for ChromaStore
```

---

## Chapter 3.3 — Knowledge graph

**Status:** Complete
**Tests:** `tests/test_graph.py` — 28 tests

### What was built

`memoryweave/graph.py`:

| Method | Purpose |
|--------|---------|
| `KnowledgeGraph.add_entities()` | Adds EntityResult list as graph nodes |
| `KnowledgeGraph.add_facts()` | Adds FactResult triples as directed edges |
| `KnowledgeGraph.query()` | String-match search over nodes and edges |
| `KnowledgeGraph.get_entity_facts()` | All facts about a specific entity |
| `KnowledgeGraph.node_count()` | Number of nodes for a session |
| `KnowledgeGraph.edge_count()` | Number of edges for a session |
| `KnowledgeGraph.delete_session()` | Wipe all graph data for a session |
| `KnowledgeGraph.save()` | Persist graph to JSON |
| `KnowledgeGraph.load()` | Load graph from JSON |

### Design decisions

**Why NetworkX?**
Pure Python, zero external services, zero configuration. Good enough for
single-user use cases with hundreds of entities. For multi-user scale
(thousands of users, millions of nodes), Neo4j would be the right move —
but that's a Phase 6+ concern.
*Decision by: Ravi Kashyap · 2026-04-03*

**Why directed graph (DiGraph)?**
Facts are directional — "Ravi likes Python" is not the same as
"Python likes Ravi". DiGraph preserves this direction, which matters
for traversal queries.
*Decision by: Ravi Kashyap · 2026-04-03*

**Why string-match query instead of semantic?**
The graph is for structured lookups, not semantic search. Semantic
search is the vector store's job. Keeping the two stores doing
different things makes the fusion step in Phase 4 more meaningful —
if both stores did the same thing, combining them would add no value.
*Decision by: Ravi Kashyap · 2026-04-03*

**Node IDs: `{label}:{text}` format**
Using `PERSON:Ravi` instead of just `Ravi` prevents collisions between
entities of different types — "Python" as a LANGUAGE and "Python" as
a PRODUCT would otherwise be the same node.
*Decision by: Ravi Kashyap · 2026-04-03*

---

## Dependencies introduced this phase

| Package | Version | Purpose |
|---------|---------|---------|
| `sentence-transformers` | >=2.2 | Vector embeddings (offline) |
| `chromadb` | >=0.4 | Persistent vector store |
| `networkx` | >=3.0 | Knowledge graph (already a torch dependency) |

---

## Test coverage after Phase 3

| Module | Coverage |
|--------|---------|
| `embedder.py` | 89% |
| `store.py` | 88% |
| `graph.py` | ~90% |
| **Total project** | **~85%** |

---

## What Phase 4 builds on top of

Phase 4 (core memory API) wires everything built in Phases 2 and 3
together into the `memory.add()` and `memory.get()` pipeline:

```
memory.add(text)
  → Extractor.extract(text)        # Phase 2
  → Embedder.embed(text)           # Phase 3.1
  → BaseStore.add(item)            # Phase 3.2
  → KnowledgeGraph.add_entities()  # Phase 3.3
  → KnowledgeGraph.add_facts()     # Phase 3.3

memory.get(query)
  → Embedder.embed(query)          # Phase 3.1
  → BaseStore.search(embedding)    # Phase 3.2
  → KnowledgeGraph.query(query)    # Phase 3.3
  → Ranker.fuse(vector, graph)     # Phase 4
  → MemoryContext                  # Phase 4
```

---

*Document created: Ravi Kashyap 2026-04-03 (Phase 3, Chapter 3.4)*
