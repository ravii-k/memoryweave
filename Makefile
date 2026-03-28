# MemoryWeave — common dev commands
# Run any target with: make <target>
# e.g. make test, make lint, make install

.PHONY: install test lint format clean help

# default target when you just run "make"
help:
	@echo "Available commands:"
	@echo "  make install   — install package in dev mode"
	@echo "  make test      — run all tests with coverage"
	@echo "  make lint      — run ruff linter"
	@echo "  make format    — run ruff formatter"
	@echo "  make clean     — remove cache and build files"

install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

# just lint, no autofix — good for checking before committing
lint:
	ruff check .

# format in place
format:
	ruff format .
	ruff check . --fix

# handy for cleaning up before a fresh install
clean:
	rm -rf .pytest_cache .ruff_cache .coverage coverage.xml
	rm -rf memoryweave.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
