# Phase 1 — Repo foundation & project setup

**Phase:** 1 of 8
**Timeline:** Week 1, Days 1–7
**Chapters:** 1.1 · 1.2 · 1.3 · 1.4
**Author:** Ravi Kashyap
**GitHub:** https://github.com/ravii-k
**Started:** 2026-03-22

---

## Overview

Phase 1 establishes every project-wide convention, tool, and scaffold that all future
phases depend on. Nothing functional is built here — but getting this right means every
future chapter has a clean, consistent foundation to build on.

The goal at the end of Phase 1: a clean GitHub repo, passing CI, an installable (empty)
Python package, and all conventions documented so any contributor can onboard instantly.

---

## Chapter 1.1 — Repo & Git setup

**Days:** 1–2
**Status:** Complete
**Author:** Ravi Kashyap · 2026-03-22

### What was built

| File / Directory | Purpose |
|-----------------|---------|
| `LICENSE` | MIT License — maximises adoption and contribution |
| `.gitignore` | Ignores Python caches, venvs, node_modules, secrets, vector store data |
| `.editorconfig` | Enforces consistent indentation and line endings across all editors |
| `README.md` | Project overview, quickstart stub, roadmap, badge placeholders |
| `CHANGELOG.md` | Version history — updated every phase end |
| `CONTRIBUTING.md` | Full contributor guide: setup, branch conventions, commit format, comment rules, docstring format, testing and doc requirements |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Structured bug report template |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Structured feature request template |
| `.github/pull_request_template.md` | PR checklist enforcing tests, docs, and comment conventions |

### Commit

```
chore(p1/ch1.1): init repo, add LICENSE, .gitignore, .editorconfig, issue templates, CONTRIBUTING.md, README, CHANGELOG, docs/phase-1-setup.md
```

---

## Chapter 1.2 — Python package skeleton

**Days:** 2–3
**Status:** Complete
**Author:** Ravi Kashyap · 2026-03-23

### What was built

| File | Purpose |
|------|---------|
| `pyproject.toml` | Modern PEP 621 package config — metadata, dependencies, ruff, pytest, mypy |
| `memoryweave/__init__.py` | Package entry point — version, author, public API exports |
| `memoryweave/config.py` | `MemoryConfig` dataclass — all SDK settings with Pydantic validation |
| `memoryweave/errors.py` | All custom exception classes — `MemoryWeaveError` and 6 subtypes |
| `memoryweave/client.py` | `MemoryWeave` main client — full docstrings, stub methods with `NotImplementedError` |
| `memoryweave/extractor.py` | `Extractor`, `EntityResult`, `FactResult` — stubs for Phase 2 |
| `memoryweave/embedder.py` | `Embedder` — stub for Phase 3 |
| `memoryweave/store.py` | `BaseStore`, `MemoryItem` — abstract interface + factory stub for Phase 3 |
| `memoryweave/graph.py` | `KnowledgeGraph` — stub for Phase 3 |
| `memoryweave/ranker.py` | `Ranker`, `MemoryContext` — stub for Phase 4 |
| `memoryweave/adapters/__init__.py` | Adapters package — stub exports for Phase 4 |
| `tests/__init__.py` | Makes tests a Python package |
| `tests/test_config.py` | 11 tests for `MemoryConfig` — defaults, custom values, validation |
| `tests/test_client.py` | 6 tests for `MemoryWeave` client — init and stub behaviour |

### Design decisions

**Why pyproject.toml over setup.py?**
`pyproject.toml` is the modern PEP 621 standard, supported by all major tools (pip,
setuptools, build, twine). `setup.py` is legacy — new projects should not use it.
*Decision by: Ravi Kashyap · 2026-03-23*

**Why Pydantic for MemoryConfig?**
Pydantic gives us free type validation, clear error messages, and IDE autocomplete for
all config fields. A plain dataclass would silently accept invalid values (e.g.
`top_k=-1`). Pydantic catches these at instantiation time.
*Decision by: Ravi Kashyap · 2026-03-23*

**Why stub methods raise NotImplementedError instead of returning None?**
Returning `None` silently would let users think the function works when it doesn't.
`NotImplementedError` with a clear message ("will be implemented in Phase 4") makes the
stub status explicit and discoverable — no surprises.
*Decision by: Ravi Kashyap · 2026-03-23*

**Why write tests now for stub code?**
Testing stubs ensures the class interfaces are correct before implementation begins.
If the stubs pass their tests, the Phase 2-4 implementations just need to replace the
`NotImplementedError` raises — the test contracts are already defined.
*Decision by: Ravi Kashyap · 2026-03-23*

**Fusion weights: 0.6 vector / 0.4 graph**
Initial values chosen based on published research showing vector search has higher
recall on open-domain queries, while graph search has higher precision on
entity-specific queries. Will be benchmarked and tuned in Phase 4.
*Decision by: Ravi Kashyap · 2026-03-23*

### Commit

```
feat(p1/ch1.2): add Python package skeleton — pyproject.toml, all module stubs, MemoryConfig, errors, 17 tests
```

---

## Chapter 1.3 — CI/CD pipeline

**Days:** 4–5
**Status:** Planned
**Author:** Ravi Kashyap

*To be documented when Chapter 1.3 is complete.*

---

## Chapter 1.4 — Config & base classes

**Days:** 6–7
**Status:** Planned
**Author:** Ravi Kashyap

*To be documented when Chapter 1.4 is complete.*

---

## Phase 1 deliverables (end of week 1)

- [x] Clean GitHub repo with all conventions in place
- [x] Python package skeleton with all module stubs
- [x] 17 tests written (all passing)
- [ ] Passing CI on every push (Chapter 1.3)
- [ ] `pip install -e .` working (Chapter 1.2 virtual env setup)
- [ ] Tagged `v0.0.1-setup` on `main` (end of Chapter 1.4)

---

## Dependencies introduced this phase

| Package | Version | Purpose |
|---------|---------|---------|
| `pydantic` | >=2.0 | Config validation and type checking |
| `pytest` | >=7.4 | Test runner (dev only) |
| `pytest-cov` | >=4.1 | Coverage reporting (dev only) |
| `pytest-asyncio` | >=0.23 | Async test support (dev only) |
| `ruff` | >=0.3 | Linting and formatting (dev only) |
| `mypy` | >=1.8 | Static type checking (dev only) |
| `pre-commit` | >=3.6 | Git hook runner (dev only) |

---

## Known limitations

- All core methods raise `NotImplementedError` — nothing functional yet.
- README badges will show errors until PyPI and npm packages are published (Phase 4/5).
- Fusion weights (0.6/0.4) are unverified defaults — will be benchmarked in Phase 4.

---

## What Phase 2 builds on top of

Phase 2 (NLP pipeline) will implement `Extractor.extract_entities()` and
`Extractor.extract_facts()`, replacing the `NotImplementedError` stubs in
`memoryweave/extractor.py`. It will also add `spaCy` as a runtime dependency
in `pyproject.toml`.

---

*Document created: Ravi Kashyap 2026-03-22 (Phase 1, Chapter 1.1)*
*Updated: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)*
