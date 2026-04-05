# MemoryWeave

> Universal long-term memory for any LLM application.

[![CI](https://github.com/ravii-k/memoryweave/actions/workflows/ci.yml/badge.svg)](https://github.com/ravii-k/memoryweave/actions)
[![Python](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12-blue)](https://pypi.org/project/memoryweave/)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-orange)](https://pypi.org/project/memoryweave/1.0.0/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

LLMs are stateless. Every conversation starts from zero. MemoryWeave fixes that.

Plug into any LLM app with **3 lines of code**. It automatically extracts entities and facts from conversations, builds a personal knowledge graph, and surfaces the most relevant context on every prompt — across sessions, users, and models.

```python
import memoryweave

memory = memoryweave.MemoryWeave()
memory.add("My name is Ravi and I prefer Python over JavaScript.")
ctx = memory.get("What language does the user prefer?")
# inject ctx.summary into your LLM system prompt
print(ctx.summary)
# → Relevant memories:
# → - My name is Ravi and I prefer Python over JavaScript. (relevance: 0.94)
```

---

## Features

- **Model-agnostic** — works with OpenAI, Anthropic, Gemini, Ollama, and any LLM
- **Dual retrieval** — combines semantic vector search with a structured knowledge graph
- **Zero config** — works out of the box with in-memory storage; swap to ChromaDB in one line
- **Multi-session** — isolated per-user memory with `session_id`
- **REST API** — FastAPI server so any language can use it
- **TypeScript SDK** — native JS/TS client for the REST API
- **Fully offline** — no API keys needed; runs on CPU with local models

---

## Installation

```bash
pip install memoryweave
python -m spacy download en_core_web_sm
```

**Optional extras:**
```bash
pip install memoryweave[server]    # FastAPI REST server
```

---

## Quick start

### Python

```python
from memoryweave import MemoryWeave, MemoryConfig

memory = MemoryWeave()
memory.add("My name is Ravi Kashyap.")
memory.add("I work at a startup building AI tools in India.")
memory.add("I prefer Python and FastAPI for backend development.")

ctx = memory.get("What does this person do for work?")
print(ctx.summary)

print(memory.stats())
# → {'session_id': 'default', 'vector_count': 3, 'node_count': 4, 'edge_count': 2}
```

### With ChromaDB persistence

```python
from memoryweave import MemoryWeave, MemoryConfig

memory = MemoryWeave(MemoryConfig(
    store_type="chroma",
    store_path="./my_memory_db",
    default_session_id="user-ravi",
))

memory.add("Ravi prefers dark mode and mechanical keyboards.")
ctx = memory.get("What are this user's preferences?")
```

### With the REST API (any language)

Start the server:
```bash
uvicorn memoryweave.server:app --reload
# → http://localhost:8000/docs
```

TypeScript:
```typescript
import { MemoryWeave } from "@memoryweave/sdk";

const memory = new MemoryWeave({ sessionId: "user-123" });
await memory.add("My name is Ravi and I prefer Python.");
const ctx = await memory.get("What language does the user prefer?");
console.log(ctx.summary);
```

curl:
```bash
curl -X POST http://localhost:8000/memory/add \
  -H "Content-Type: application/json" \
  -d '{"text": "Ravi prefers Python.", "session_id": "demo"}'
```

---

## How it works

```
memory.add(text)
  │
  ├─ Extractor (spaCy)              → entities + facts
  ├─ Embedder (sentence-transformers) → 384-dim vector
  ├─ BaseStore (InMemory/Chroma)    → vector storage
  └─ KnowledgeGraph (NetworkX)     → entity + fact graph

memory.get(query)
  │
  ├─ Embedder → query vector
  ├─ BaseStore.search()  → top-k similar memories
  ├─ KnowledgeGraph.query() → related facts
  └─ Ranker.fuse() → weighted blend → MemoryContext
```

**Fusion formula:** `score = 0.6 × vector_score + 0.4 × graph_score`

---

## Configuration

```python
from memoryweave import MemoryConfig

config = MemoryConfig(
    store_type="memory",             # "memory" | "chroma"
    store_path="./mw_db",            # path for chroma
    embedding_model="all-MiniLM-L6-v2",
    spacy_model="en_core_web_sm",
    top_k=5,
    vector_weight=0.6,
    graph_weight=0.4,
    default_session_id="default",
)
```

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/memory/add` | Add a memory |
| `POST` | `/memory/get` | Retrieve context |
| `DELETE` | `/memory/forget` | Wipe a session |
| `GET` | `/memory/stats` | Session stats |

Interactive docs at **http://localhost:8000/docs**

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
```

**Test coverage:** 225 tests · 91% coverage · CI green on Python 3.10/3.11/3.12 · Live on [PyPI](https://pypi.org/project/memoryweave/1.0.0/)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
git clone https://github.com/ravii-k/memoryweave.git
cd memoryweave
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,server]"
python -m spacy download en_core_web_sm
pytest tests/ -v
```

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built by [Ravi Kashyap](https://github.com/ravii-k) · v1.0.0 shipped April 2026*
