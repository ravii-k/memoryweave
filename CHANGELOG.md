# Changelog

All notable changes to MemoryWeave are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.0.0] — 2026-04-04 — Production release

### Summary
Full end-to-end LLM memory SDK. Plug in with 3 lines of code.
225 tests passing. 90%+ coverage. CI green on Python 3.10/3.11/3.12.

### Added — Phase 8 (Launch)
- Version bumped to `1.0.0` — production stable
- `pyproject.toml` — full PyPI classifiers, optional extras, scripts
- `CONTRIBUTING.md` — updated contribution guide

### Added — Phase 7 (Documentation)
- `README.md` — comprehensive project README with badges, quickstart, architecture
- `docs/quickstart.md` — OpenAI integration guide, multi-user sessions, ChromaDB example

### Added — Phase 6 (FastAPI REST server)
- `memoryweave/server.py` — FastAPI REST API
- Endpoints: `/health`, `/memory/add`, `/memory/get`, `/memory/forget`, `/memory/stats`
- CORS middleware, per-session client management
- `tests/test_server.py` — 16 server endpoint tests

### Added — Phase 5 (TypeScript SDK)
- `sdk/typescript/` — full TypeScript/JavaScript client
- Mirrors Python API: `add()`, `get()`, `forget()`, `stats()`, `isHealthy()`
- 20 Jest tests with mocked fetch
- Works with Node.js 18+ (native fetch)

### Added — Phase 4 (Core memory API)
- `memoryweave/client.py` — `MemoryWeave` with `add()`, `get()`, `forget()`, `stats()`
- `memoryweave/ranker.py` — weighted fusion ranker (0.6 vector + 0.4 graph)
- `memoryweave/ranker.py` — `MemoryContext` result object
- Lazy-loading of all heavy components (spaCy, sentence-transformers)
- `examples/basic_usage.py` — working demo script

### Added — Phase 3 (Storage layer)
- `memoryweave/embedder.py` — sentence-transformers, all-MiniLM-L6-v2, 384-dim
- `memoryweave/store.py` — `InMemoryStore` and `ChromaStore` with factory
- `memoryweave/graph.py` — `KnowledgeGraph` with NetworkX DiGraph, save/load

### Added — Phase 2 (NLP pipeline)
- `memoryweave/extractor.py` — spaCy entity + fact extraction pipeline
- `EntityResult`, `FactResult` dataclasses
- `extract()` convenience method — single spaCy parse for both pipelines

### Added — Phase 1 (Foundation)
- Full Python package skeleton with all module stubs
- `MemoryConfig` with Pydantic v2 validation
- GitHub Actions CI (Python 3.10/3.11/3.12)
- `memoryweave/logger.py` — structured logging

---

*Project started: Ravi Kashyap, March 2026*
*GitHub: https://github.com/ravii-k/memoryweave*
