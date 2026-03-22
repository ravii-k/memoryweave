# Contributing to MemoryWeave

Thank you for your interest in contributing. MemoryWeave is built in the open and every
contribution — bug reports, docs improvements, new adapters, or core features — matters.

---

## Table of contents

1. [Code of conduct](#code-of-conduct)
2. [How to contribute](#how-to-contribute)
3. [Development setup](#development-setup)
4. [Branch & commit conventions](#branch--commit-conventions)
5. [Code style](#code-style)
6. [Code comment conventions](#code-comment-conventions)
7. [Testing requirements](#testing-requirements)
8. [Documentation requirements](#documentation-requirements)
9. [Submitting a pull request](#submitting-a-pull-request)
10. [Project structure](#project-structure)

---

## Code of conduct

Be kind, be respectful, be constructive. We are here to build something great together.
Harassment, discrimination, or dismissive behaviour will not be tolerated.

---

## How to contribute

### Reporting bugs
Open an issue using the **Bug report** template. Include a minimal reproduction case.

### Requesting features
Open an issue using the **Feature request** template. Explain the problem it solves, not
just the solution you want.

### Contributing code
1. Check open issues and the public roadmap before starting.
2. Comment on the issue you want to work on so nobody duplicates effort.
3. Fork the repo and create a branch following the naming convention below.
4. Write code, tests, and docs together — not tests and docs after.
5. Open a PR against `dev`, not `main`.

---

## Development setup

### Requirements
- Python 3.10 or 3.11
- Node.js 18+ (for the TypeScript SDK)
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/ravii-k/memoryweave.git
cd memoryweave

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# Install development dependencies
pip install -e "packages/core[dev]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Verify everything works
pytest packages/core/tests/ -v
```

### Running tests

```bash
# All tests
pytest

# Single file
pytest packages/core/tests/test_extractor.py -v

# With coverage
pytest --cov=memoryweave --cov-report=term-missing
```

### Linting

```bash
ruff check .          # lint
ruff format .         # format (replaces black)
```

Pre-commit hooks run both automatically on every commit.

---

## Branch & commit conventions

### Branch names

```
phase/1-foundation         # phase branches
fix/entity-extractor-utf8  # bug fixes
feat/mistral-adapter       # new features
docs/storage-layer         # documentation
```

### Commit message format

```
type(phase/chapter): short description (max 72 chars)

Optional body: what changed and why. Wrap at 72 chars.
Refs: #issue-number
```

**Types:** `feat` · `fix` · `docs` · `test` · `refactor` · `chore` · `perf`

**Examples:**
```
feat(p2/ch2.1): implement entity extractor using spaCy
fix(p3/ch3.2): handle ChromaDB connection timeout on cold start
docs(p4/ch4.2): document MemoryContext response fields
test(p2/ch2.1): add 12 unit tests for edge cases in entity extraction
```

### Rules
- Minimum 1 commit per working day.
- Never commit directly to `main`. Always go through `dev`.
- Never commit secrets, API keys, or `.env` files.

---

## Code style

- **Formatter:** `ruff format` (88-char line length)
- **Linter:** `ruff check`
- **Type hints:** required on all public function signatures
- **Python version:** 3.10+ syntax only

---

## Code comment conventions

### Standard inline comment
Add your name and date whenever you write significant logic or change existing logic.

```python
# Ravi Kashyap YYYY-MM-DD - Why this decision was made
result = self._fuse_scores(vector_results, graph_results)
```

### Changing existing code in a later phase
Keep the original comment and add a new one directly below it.

```python
# Ravi Kashyap 2025-03-22 - Original fusion logic
# Ravi Kashyap 2025-04-10 - Phase 6: added decay weighting,
#   see docs/memory-decay.md for formula details
result = self._fuse_with_decay(vector_results, graph_results)
```

### TODO comments
All TODOs must include name, date, and a GitHub issue reference.

```python
# TODO Ravi Kashyap 2025-03-25 - Add async version. Tracked: #42
```

### Docstrings
Every public function and class requires a docstring in the format below.
No chapter may be merged without 100% public API docstring coverage.

```python
def add(self, text: str, session_id: str = "default") -> None:
    """Add a memory from raw text.

    Runs the full pipeline: NLP extraction -> embedding
    -> vector store -> knowledge graph update.

    Args:
        text: Raw text to extract memory from.
        session_id: Namespace for multi-user isolation.
            Defaults to "default".

    Raises:
        MemoryWeaveError: If the NLP pipeline fails to parse text.

    Added: Ravi Kashyap 2025-03-24 (Phase 4, Chapter 4.1)
    """
```

---

## Testing requirements

- New features must include tests in `packages/core/tests/`.
- Bug fixes must include a regression test that would have caught the bug.
- Minimum coverage for any PR touching core logic: 80%.
- Tests must pass on Python 3.10 and 3.11.

---

## Documentation requirements

- Every new public function: docstring (see above).
- Every new module: module-level docstring explaining its purpose.
- Every chapter completion: update or create the relevant file in `docs/`.
- Breaking changes: update `docs/migration.md`.
- All changes: update `CHANGELOG.md` under the `[Unreleased]` section.

---

## Submitting a pull request

1. Ensure all tests pass locally: `pytest`
2. Ensure no lint errors: `ruff check .`
3. Fill in the PR template completely.
4. Open the PR against `dev`, not `main`.
5. Link the issue your PR resolves: `Closes #42`
6. A maintainer will review within 3 business days.

---

## Project structure

```
memoryweave/
├── packages/
│   ├── core/             # Python SDK
│   │   ├── memoryweave/  # source code
│   │   └── tests/        # pytest tests
│   ├── js/               # TypeScript SDK
│   └── server/           # Optional FastAPI server
├── docs/                 # Markdown documentation
├── examples/             # Runnable demo projects
└── .github/              # CI workflows and templates
```

---

*Document created: Ravi Kashyap 2025-03-22 (Phase 1, Chapter 1.1)*
*Last updated: Ravi Kashyap 2025-03-22*
