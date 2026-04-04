## [0.1.0] — 2026-04-04

### Added — Phase 6 (FastAPI REST server)
- `memoryweave/server.py` — FastAPI REST API with `/memory/add`, `/memory/get`, `/memory/forget`, `/memory/stats`, `/health`
- CORS middleware enabled for all origins (tighten in production)
- Per-session MemoryWeave client management
- `tests/test_server.py` — 16 server endpoint tests
- FastAPI interactive docs at `/docs` and `/redoc`

### Added — Phase 5 (TypeScript SDK)
- `sdk/typescript/src/client.ts` — full TypeScript client wrapping the REST API
- `sdk/typescript/src/types.ts` — TypeScript types matching Python API
- `sdk/typescript/src/index.ts` — public exports
- `sdk/typescript/tests/client.test.ts` — 20 Jest tests with mocked fetch
- `sdk/typescript/package.json`, `tsconfig.json`, `README.md`

### Added — Phase 7 (Documentation)
- `README.md` — comprehensive project README with quickstart, API docs, architecture diagram
- `docs/quickstart.md` — step-by-step guide including OpenAI integration example

# Changelog

All notable changes to MemoryWeave are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
### Added
- `memoryweave/client.py` — full `MemoryWeave` client with `add()`, `get()`, `forget()`, `stats()`
- `memoryweave/ranker.py` — `Ranker` with weighted vector+graph fusion, `MemoryContext` result
- Lazy-loading of spaCy, sentence-transformers, and store on first use
- Full public API exposed in `__init__.py` — `MemoryWeave`, `MemoryConfig`, `MemoryContext`, `configure_logging`
- `examples/basic_usage.py` — demo script showing add/get pipeline
- `tests/test_client.py` — 21 end-to-end client tests
- `tests/test_ranker.py` — 13 ranker and MemoryContext tests
- Version bumped to `0.1.0`

### Changed
- `memoryweave/__init__.py` — now exports full public API
- `pyproject.toml` — version bumped to `0.1.0`

### Added
- `memoryweave/graph.py` — full KnowledgeGraph implementation using NetworkX
- `KnowledgeGraph.add_entities()` — adds EntityResult nodes to session graph
- `KnowledgeGraph.add_facts()` — adds FactResult triples as directed edges
- `KnowledgeGraph.query()` — string-match fact retrieval
- `KnowledgeGraph.get_entity_facts()` — lookup all facts for a specific entity
- `KnowledgeGraph.save()` / `.load()` — JSON persistence
- `memoryweave/store.py` — full InMemoryStore and ChromaStore implementations
- `memoryweave/embedder.py` — full Embedder with sentence-transformers
- `tests/test_graph.py` — 28 knowledge graph tests
- `tests/test_store.py` — 32 vector store tests
- `tests/test_embedder.py` — 24 embedder tests
- `docs/storage-layer.md` — full Phase 3 documentation
- networkx added to runtime dependencies

### Changed
- `pyproject.toml` — added sentence-transformers, chromadb, networkx deps
- CI pipeline — downloads spaCy model, sentence-transformers model, chromadb

## [Unreleased]

### Added
- `memoryweave/extractor.py` — full spaCy NLP pipeline implementation
- `EntityResult` and `FactResult` dataclasses
- `Extractor.extract()` convenience method — single spaCy parse for both pipelines
- `Extractor._extract_entities_from_doc()` and `_extract_facts_from_doc()` private methods
- `tests/test_extractor.py` — 25 entity and fact extraction tests
- `tests/test_extractor_pipeline.py` — 18 pipeline, confidence, and edge case tests
- `tests/test_extractor_accuracy.py` — 18 accuracy benchmark tests
- `docs/nlp-pipeline.md` — full Phase 2 documentation
- spaCy model download step added to CI pipeline

### Changed
- `pyproject.toml` — added `spacy>=3.7` as runtime dependency

### Added
- `memoryweave/logger.py` — logging setup, `get_logger()`, `configure_logging()`
- `MEMORYWEAVE_LOG_LEVEL` env var support for zero-config logging
- `configure_logging` exposed in public API via `__init__.py`
- `tests/test_logger.py` — 9 tests for logging module

---

## [0.0.1-setup] — 2026-03-28

### Added
- GitHub Actions CI — tests on Python 3.10/3.11/3.12 + lint on every push
- `Makefile` — `make test`, `make lint`, `make format`, `make clean`
- `.env.example` — template for API keys and config
- `.pre-commit-config.yaml` — ruff + ruff-format + pre-commit-hooks
- Python package skeleton — all module stubs with full docstrings
- `MemoryConfig` with Pydantic v2 validation including weight sum validator
- 23 tests passing across `test_config.py` and `test_client.py`
- Custom exception hierarchy — `MemoryWeaveError` and 6 subclasses
- `MemoryContext`, `MemoryItem`, `BaseStore`, `Ranker` dataclass stubs
- MIT LICENSE, `.gitignore`, `.editorconfig`
- GitHub issue templates, pull request template
- `CONTRIBUTING.md` with full conventions guide
- `docs/phase-1-setup.md` — Phase 1 documentation

### Fixed
- Build backend corrected to `setuptools.build_meta`
- Author email updated to `kashyap01212@gmail.com`
- Python classifiers extended to include 3.13 and 3.14
- Ruff ignore rules cleaned up — removed deprecated `ANN101`

---

*Changelog started: Ravi Kashyap 2026-03-22 (Phase 1, Chapter 1.1)*
