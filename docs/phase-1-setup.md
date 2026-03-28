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
**Status:** Complete ✅
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
**Status:** Complete ✅
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
| `tests/test_config.py` | 17 tests for `MemoryConfig` — defaults, custom values, validation |
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
**Status:** Complete ✅
**Author:** Ravi Kashyap · 2026-03-25

### What was built

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Runs tests across Python 3.10–3.12 and lint on every push |
| `Makefile` | Local shortcuts: `make test`, `make lint`, `make format`, `make clean` |
| `.env.example` | Template documenting every env var the SDK will need |
| `.pre-commit-config.yaml` | Runs ruff + ruff-format automatically before every commit |

### CI workflow

The `ci.yml` defines two parallel jobs that run on every push to any branch and on
PRs targeting `dev` or `main`.

**`test` job** — matrix across Python 3.10, 3.11, 3.12:
```bash
pip install -e ".[dev]"
pytest tests/ -v --cov=memoryweave --cov-report=xml --cov-fail-under=20
```

**`lint` job:**
```bash
ruff check .
ruff format --check .
```

### Pre-commit hooks

Install once after cloning:
```bash
source .venv/bin/activate
pre-commit install
```

From that point on, `ruff check` and `ruff format` run automatically before every
commit. If either fails the commit is blocked — the output tells you exactly what to fix.

### Makefile targets

```bash
make test      # pytest with coverage
make lint      # ruff check (errors only, no auto-fix)
make format    # ruff format --check (shows diff, no auto-fix)
make clean     # remove __pycache__, .pytest_cache, .coverage, dist/
```

To auto-fix locally (outside of make):
```bash
ruff format .
ruff check . --fix
```

### Coverage threshold

Currently `--cov-fail-under=20`. Will increase each phase as real implementation
replaces stubs. Target at v1.0.0: ≥ 90%.

### Design decisions

**Why a matrix across 3.10, 3.11, 3.12 and not just the latest?**
MemoryWeave targets a broad audience. Pinning CI to 3.12 only would let regressions
slip in for users on 3.10 or 3.11 — catching them in CI is cheaper than a bug report.
Python 3.14 is excluded from the matrix because GitHub Actions runners don't have a
stable 3.14 image yet; it's covered locally during development.
*Decision by: Ravi Kashyap · 2026-03-25*

**Why pre-commit instead of just relying on CI lint?**
CI lint catches problems after a push — pre-commit catches them before the commit
lands in git history at all. Keeping history clean matters more as the project grows
and contributors join.
*Decision by: Ravi Kashyap · 2026-03-25*

### Commit

```
chore(p1/ch1.3): add CI workflow, Makefile, .env.example, pre-commit config
```

---

## Chapter 1.4 — Logging & base interface review

**Days:** 6–7
**Status:** Complete ✅
**Author:** Ravi Kashyap · 2026-03-28

### What was built

| File | Purpose |
|------|---------|
| `memoryweave/logger.py` | Library-scoped logging with `get_logger()` and `configure_logging()` |
| `tests/test_logger.py` | 11 tests — level setting, idempotency, env var override, propagation |

### Logging design

MemoryWeave uses Python's standard `logging` module with a single root logger named
`memoryweave`. Every sub-module gets its own child logger by calling:

```python
from memoryweave.logger import get_logger
log = get_logger(__name__)
```

This keeps library output completely separate from application logs. Users control
verbosity with one call:

```python
import logging
from memoryweave.logger import configure_logging

configure_logging(logging.DEBUG)    # verbose — see everything
configure_logging(logging.WARNING)  # default — silent in production
```

Or via environment variable — no code change needed in deployed apps:
```bash
export MEMORYWEAVE_LOG_LEVEL=DEBUG
```

### Design decisions

**Why not call configure_logging() on import?**
That would be rude. Libraries that configure logging on import stomp over whatever
the application has set up. It's the user's app — they own the logging config.
We provide the tools; they decide when to use them.
*Decision by: Ravi Kashyap · 2026-03-28*

**Why root.propagate = False?**
Without this, every MemoryWeave log message bubbles up to the Python root logger and
gets printed twice if the application has its own handler. Setting propagate=False
keeps our messages in the `memoryweave` namespace where they belong.
*Decision by: Ravi Kashyap · 2026-03-28*

**Why an idempotent _configured flag?**
configure_logging() might get called in tests, in notebooks, and in application startup
— sometimes more than once. Without the flag, each call adds another StreamHandler
and you get duplicate lines. The force=True escape hatch handles the cases (tests,
REPL sessions) where you genuinely need to reconfigure.
*Decision by: Ravi Kashyap · 2026-03-28*

### Base interface audit

All five core interfaces confirmed as complete stubs. Every abstract method raises
`NotImplementedError` with a comment pointing to the phase where it gets implemented.
No silent `None` returns anywhere.

| Interface | File | Implemented in |
|-----------|------|---------------|
| `BaseStore` | `store.py` | Phase 3, Chapter 3.2 |
| `Extractor` | `extractor.py` | Phase 2, Chapters 2.1–2.2 |
| `Embedder` | `embedder.py` | Phase 3, Chapter 3.1 |
| `KnowledgeGraph` | `graph.py` | Phase 3, Chapter 3.3 |
| `Ranker` | `ranker.py` | Phase 4, Chapter 4.2 |

### Test count at end of Phase 1

| Module | Tests |
|--------|-------|
| `test_config.py` | 17 |
| `test_client.py` | 6 |
| `test_logger.py` | 11 |
| **Total** | **34** |

Coverage rises to ~35% with the logger tests added.

### Phase 1 wrap-up — merge and tag

After Chapter 1.4, run the following to close out Phase 1:

**1. Open PR on GitHub:** `phase/1-foundation` → `dev`, review and merge.

**2. Open PR on GitHub:** `dev` → `main`, review and merge.

**3. Tag the release locally:**
```bash
git checkout main
git pull origin main
git tag -a v0.0.1-setup -m "chore: Phase 1 foundation complete"
git push origin v0.0.1-setup
```

### Commit

```
feat(p1/ch1.4): add logger module, confirm base interfaces, complete Phase 1
```

---

## Phase 1 deliverables

- [x] Clean GitHub repo with all conventions in place
- [x] Python package skeleton with all module stubs
- [x] 34 tests written (all passing)
- [x] Passing CI on every push
- [x] `pip install -e ".[dev]"` working
- [x] Tagged `v0.0.1-setup` on `main`

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
- Coverage threshold set to 20% — will increase each phase, targeting ≥ 90% at v1.0.0.

---

## What Phase 2 builds on top of

Phase 2 (NLP pipeline) will implement `Extractor.extract_entities()` and
`Extractor.extract_facts()`, replacing the `NotImplementedError` stubs in
`memoryweave/extractor.py`. It will also add `spaCy` and `GLiNER` as runtime
dependencies in `pyproject.toml`.

---

*Document created: Ravi Kashyap 2026-03-22 (Phase 1, Chapter 1.1)*
*Updated: Ravi Kashyap 2026-03-23 (Phase 1, Chapter 1.2)*
*Updated: Ravi Kashyap 2026-03-25 (Phase 1, Chapter 1.3)*
*Updated: Ravi Kashyap 2026-03-28 (Phase 1, Chapter 1.4)*
