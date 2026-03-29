# Changelog

All notable changes to MemoryWeave are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

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
