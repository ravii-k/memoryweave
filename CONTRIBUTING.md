# Contributing to MemoryWeave

Thank you for your interest in contributing! This guide will help you get started.

---

## Development setup

```bash
git clone https://github.com/ravii-k/memoryweave.git
cd memoryweave

python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

pip install -e ".[dev,server]"
python -m spacy download en_core_web_sm

pre-commit install
```

## Running tests

```bash
# all tests
pytest tests/ -v

# specific module
pytest tests/test_client.py -v

# with coverage
pytest tests/ --cov=memoryweave --cov-report=html
open htmlcov/index.html
```

## TypeScript SDK tests

```bash
cd sdk/typescript
npm install
npm test
```

## Code style

This project uses `ruff` for linting and formatting. Pre-commit hooks
run automatically on every commit.

```bash
# lint
ruff check .

# format
ruff format .

# or via Makefile
make lint
make format
```

## Project structure

```
memoryweave/
├── memoryweave/        # Python package
│   ├── client.py       # Main MemoryWeave client
│   ├── config.py       # MemoryConfig (Pydantic v2)
│   ├── embedder.py     # sentence-transformers
│   ├── extractor.py    # spaCy NLP pipeline
│   ├── graph.py        # NetworkX knowledge graph
│   ├── logger.py       # Logging setup
│   ├── ranker.py       # Fusion ranker + MemoryContext
│   ├── server.py       # FastAPI REST server
│   └── store.py        # InMemoryStore + ChromaStore
├── tests/              # Python tests
├── sdk/typescript/     # TypeScript SDK
├── examples/           # Usage examples
└── docs/               # Documentation
```

## Commit conventions

```
type(scope): description

Types: feat, fix, docs, test, refactor, chore, perf
Scope: module name or phase/chapter reference

Examples:
  feat(client): add batch add() method
  fix(store): handle empty session on search
  docs(readme): add OpenAI integration example
  test(server): add auth endpoint tests
```

## Pull request process

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Write tests for your changes
4. Ensure all tests pass: `pytest tests/ -v`
5. Run linting: `ruff check . && ruff format .`
6. Submit a PR to the `dev` branch with a clear description

## Reporting issues

Use [GitHub Issues](https://github.com/ravii-k/memoryweave/issues). Include:

- Python version and OS
- Steps to reproduce
- Expected vs actual behaviour
- Relevant error output

---

*Author: Ravi Kashyap — [github.com/ravii-k](https://github.com/ravii-k)*
