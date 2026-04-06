# MemoryWeave
---
> *We are all living in a simulation*
---
> Give your LLM a long-term memory in three lines of code.

[![CI](https://github.com/ravii-k/memoryweave/actions/workflows/ci.yml/badge.svg)](https://github.com/ravii-k/memoryweave/actions)
[![PyPI](https://img.shields.io/pypi/v/memoryweave?color=orange)](https://pypi.org/project/memoryweave/)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13%20|%203.14-blue)](https://pypi.org/project/memoryweave/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)](https://github.com/ravii-k/memoryweave/actions)

---

LLMs are stateless. Every conversation starts from scratch. MemoryWeave fixes that.

It sits between your app and any LLM — extracting facts from conversations, building a personal knowledge graph, and surfacing the most relevant context on every call. No external services, no API keys, no infrastructure required.

```python
from memoryweave import MemoryWeave

memory = MemoryWeave()
memory.add("My name is Ravi. I prefer Python and FastAPI.")
ctx = memory.get("What stack should I recommend?")

# ctx.summary is ready to paste into any system prompt
print(ctx.summary)
# → Relevant memories:
# → - My name is Ravi. I prefer Python and FastAPI. (relevance: 0.94)
```

---

## Why MemoryWeave

Most memory solutions either require a cloud service, only do vector search, or need you to manage prompts manually. MemoryWeave is different:

- **Dual retrieval** — combines semantic vector search with a structured knowledge graph. Vector search finds similar text; the graph finds related facts. A weighted ranker fuses both.
- **Fully offline** — sentence-transformers and spaCy run locally. No API keys, no data sent anywhere.
- **Zero boilerplate** — one `add()` call runs the full NLP pipeline. One `get()` call returns a ready-to-inject context string.
- **Multi-session** — each user gets isolated memory via `session_id`. Sessions never bleed into each other.
- **Deduplication** — identical or near-identical text is detected and skipped automatically (cosine similarity ≥ 0.98).
- **Polyglot** — a FastAPI REST server and TypeScript SDK let any language use it.

---

## Installation

```bash
pip install memoryweave
python -m spacy download en_core_web_sm
```

For the REST server:

```bash
pip install "memoryweave[server]"
```

---

## Quick start

### Basic usage

```python
from memoryweave import MemoryWeave, MemoryConfig

memory = MemoryWeave()

memory.add("My name is Ravi Kashyap.")
memory.add("I work on AI tools and prefer Python over JavaScript.")
memory.add("I use FastAPI for APIs and ChromaDB for vector storage.")

ctx = memory.get("What does this person prefer for backend development?")
print(ctx.summary)
print(ctx.has_results)   # True
print(memory.stats())    # {'vector_count': 3, 'node_count': 7, 'edge_count': 3, ...}
```

### Plug into OpenAI

```python
from openai import OpenAI
from memoryweave import MemoryWeave
from memoryweave.adapters.openai import OpenAIAdapter

memory = MemoryWeave()
adapter = OpenAIAdapter(memory, system_prompt="You are a helpful assistant.")
client = OpenAI()

def chat(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    messages = adapter.prepare(messages)   # injects memory into system prompt
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    adapter.remember(messages)             # stores the turn for next time
    return response.choices[0].message.content
```

### Plug into Anthropic

```python
import anthropic
from memoryweave import MemoryWeave
from memoryweave.adapters.anthropic import AnthropicAdapter

memory = MemoryWeave()
adapter = AnthropicAdapter(memory)
client = anthropic.Anthropic()

messages = [{"role": "user", "content": "What stack should I use?"}]
system, messages = adapter.prepare(messages)   # returns (system_string, messages)

response = client.messages.create(
    model="claude-opus-4-6",
    system=system,
    messages=messages,
    max_tokens=1024,
)
adapter.remember(messages)
```

### Persistent storage with ChromaDB

```python
from memoryweave import MemoryWeave, MemoryConfig

memory = MemoryWeave(MemoryConfig(
    store_type="chroma",
    store_path="./memory_db",
    default_session_id="user-ravi",
))

memory.add("Ravi prefers dark mode and mechanical keyboards.")
# Memories survive restarts — the ChromaDB files are written to ./memory_db
```

### Multi-user sessions

```python
def get_memory(user_id: str) -> MemoryWeave:
    return MemoryWeave(MemoryConfig(default_session_id=user_id))

alice = get_memory("alice")
bob   = get_memory("bob")

alice.add("Alice likes TypeScript.")
bob.add("Bob prefers Rust.")

# Sessions are fully isolated — no cross-user leakage
print(alice.get("language").summary)  # → TypeScript
print(bob.get("language").summary)    # → Rust
```

### Async support

```python
memory = MemoryWeave()

await memory.async_add("Ravi prefers async Python.")
ctx = await memory.async_get("What does Ravi prefer?")
await memory.async_forget()
```

### REST API

Start the server:

```bash
# Dev mode (no auth)
uvicorn memoryweave.server:app --reload

# Production mode (with API key)
MEMORYWEAVE_API_KEY=my-secret uvicorn memoryweave.server:app
```

Interactive docs at **http://localhost:8000/docs**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (always public) |
| `POST` | `/memory/add` | Add a memory |
| `POST` | `/memory/get` | Retrieve context |
| `DELETE` | `/memory/forget` | Wipe a session |
| `GET` | `/memory/stats` | Session stats |

When `MEMORYWEAVE_API_KEY` is set, all `/memory/*` endpoints require the `X-API-Key` header.

### TypeScript / JavaScript

```bash
npm install @memoryweave/sdk
```

```typescript
import { MemoryWeave } from "@memoryweave/sdk";

const memory = new MemoryWeave({ baseUrl: "http://localhost:8000", sessionId: "user-1" });

await memory.add("Ravi prefers Python.");
const ctx = await memory.get("What language?");
console.log(ctx.summary);
```

---

## How it works

```
memory.add(text)
  │
  ├── spaCy NLP          extract entities + subject-verb-object facts
  ├── sentence-transformers   embed text → 384-dim vector
  ├── Vector store        save embedding (InMemory or ChromaDB)
  └── Knowledge graph     add entities and facts as nodes/edges (NetworkX)

memory.get(query)
  │
  ├── Embed query
  ├── Vector search       top-k similar memories by cosine similarity
  ├── Graph query         related facts by keyword overlap
  └── Ranker              fuse scores → 0.6 × vector + 0.4 × graph → MemoryContext
```

The `MemoryContext` object returned by `get()` contains:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | `str` | Ready-to-inject string for your system prompt |
| `entries` | `list` | Vector search results with scores |
| `facts` | `list` | Graph facts with scores |
| `scores` | `list` | Final fusion scores |
| `has_results` | `bool` | False if no memories found |

---

## Configuration

```python
from memoryweave import MemoryConfig

config = MemoryConfig(
    store_type="memory",              # "memory" (default) or "chroma"
    store_path="./mw_db",             # only used when store_type="chroma"
    embedding_model="all-MiniLM-L6-v2",  # any sentence-transformers model
    spacy_model="en_core_web_sm",     # any spaCy model
    top_k=5,                          # memories to retrieve per get()
    vector_weight=0.6,                # fusion weight for vector search
    graph_weight=0.4,                 # fusion weight for graph search
    default_session_id="default",     # session namespace
)
```

---

## Project status

```
✅ Phase 1 — Foundation
✅ Phase 2 — NLP extraction pipeline (spaCy)
✅ Phase 3 — Storage layer (vector store + knowledge graph)
✅ Phase 4 — Core memory API v0.1.0
✅ Phase 5 — TypeScript SDK
✅ Phase 6 — FastAPI REST server
✅ Phase 7 — Documentation
✅ Phase 8 — Launch v1.0.0
✅ Phase 9 — Deduplication, async methods, LLM adapters, server auth v1.1.0
```

**248 tests · 91% coverage · CI green on Python 3.10 / 3.11 / 3.12**

---

## Contributing

```bash
git clone https://github.com/ravii-k/memoryweave.git
cd memoryweave

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,server]"
python -m spacy download en_core_web_sm

pre-commit install
pytest tests/ -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions, branch strategy, and PR guidelines.

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Ravi Kashyap](https://github.com/ravii-k) · Meerut, India · Started March 2026*
