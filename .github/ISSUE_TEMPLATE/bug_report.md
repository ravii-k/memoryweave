---
name: Bug report
about: Something is broken — help us fix it
title: "[BUG] "
labels: bug
assignees: ''
---

## Describe the bug
A clear description of what the bug is.

## To reproduce
Steps to reproduce the behaviour:

```python
import memoryweave

memory = memoryweave.MemoryWeave()
memory.add("...")      # what you ran
ctx = memory.get("...") # what failed
```

## Expected behaviour
What you expected to happen.

## Actual behaviour
What actually happened. Include the full error traceback if applicable.

```
Traceback (most recent call last):
  ...
```

## Environment
- MemoryWeave version: (run `python -c "import memoryweave; print(memoryweave.__version__)"`)
- Python version:
- OS:
- LLM adapter used (OpenAI / Anthropic / Ollama / other):
- Vector store used (Chroma / Qdrant / in-memory):

## Additional context
Any other context, screenshots, or notes.
