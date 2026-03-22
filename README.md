# MemoryWeave

> Universal long-term memory for any LLM application.

[![PyPI version](https://img.shields.io/pypi/v/memoryweave?style=flat-square)](https://pypi.org/project/memoryweave/)
[![npm version](https://img.shields.io/npm/v/memoryweave?style=flat-square)](https://npmjs.com/package/memoryweave)
[![CI](https://img.shields.io/github/actions/workflow/status/ravii-k/memoryweave/ci.yml?style=flat-square)](https://github.com/ravii-k/memoryweave/actions)
[![Coverage](https://img.shields.io/codecov/c/github/ravii-k/memoryweave?style=flat-square)](https://codecov.io/gh/ravii-k/memoryweave)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue?style=flat-square)](https://python.org)

---

LLMs are stateless. Every conversation starts from zero. MemoryWeave fixes that.

Plug it into any LLM app with 3 lines of code. It automatically extracts entities and
facts from conversations, builds a personal knowledge graph, and surfaces the most
relevant context on every prompt — across sessions, users, and models.

```python
import memoryweave

memory = memoryweave.MemoryWeave()
memory.add("My name is Alex and I prefer Python over JavaScript.")
ctx = memory.get("What language does the user prefer?")
# → Injects: "User is Alex. Prefers Python." into your next prompt
```

---

## Features

- **Model-agnostic** — works with OpenAI, Anthropic, Gemini, Mistral, Ollama, and any OpenAI-compatible API
- **Dual storage** — combines semantic vector search with a structured knowledge graph for higher-quality retrieval
- **Zero config** — works out of the box with in-memory or ChromaDB storage; swap backends in one line
- **Multi-user** — session namespacing for isolated per-user memory
- **Self-hostable** — run entirely locally, no data leaves your machine
- **Python + TypeScript** — native SDKs for both ecosystems

---

## Installation

```bash
pip install memoryweave
```

```bash
npm install memoryweave
```

---

## Quickstart

> Full guides in [docs/quickstart.md](docs/quickstart.md)

```python
from memoryweave import MemoryWeave
from openai import OpenAI

memory = MemoryWeave()           # in-memory store, no config needed
client = OpenAI()

def chat(user_message: str) -> str:
    memory.add(user_message)
    ctx = memory.get(user_message)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Context:\n{ctx.summary}"},
            {"role": "user",   "content": user_message},
        ]
    )
    return response.choices[0].message.content
```

---

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/quickstart.md](docs/quickstart.md) | Get running in 5 minutes |
| [docs/installation.md](docs/installation.md) | Full install + config options |
| [docs/api-reference.md](docs/api-reference.md) | All methods and return types |
| [docs/nlp-pipeline.md](docs/nlp-pipeline.md) | How extraction works |
| [docs/storage-layer.md](docs/storage-layer.md) | Vector + graph storage |
| [docs/typescript-sdk.md](docs/typescript-sdk.md) | TypeScript / Next.js guide |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Supported LLMs & stores

| LLM | Status |
|-----|--------|
| OpenAI (GPT-4o, GPT-4) | Planned (Phase 4) |
| Anthropic (Claude) | Planned (Phase 4) |
| Ollama (local models) | Planned (Phase 4) |
| Mistral | Planned (Phase 6) |
| Gemini | Planned (Phase 5) |

| Vector store | Status |
|-------------|--------|
| In-memory (default) | Planned (Phase 3) |
| ChromaDB | Planned (Phase 3) |
| Qdrant | Planned (Phase 3) |
| Pinecone | Roadmap |

---

## Roadmap

- [x] Phase 1 — Repo foundation & project setup
- [ ] Phase 2 — NLP extraction pipeline
- [ ] Phase 3 — Storage layer (vector + graph)
- [ ] Phase 4 — Core memory API (`memory.add` / `memory.get`)
- [ ] Phase 5 — TypeScript SDK
- [ ] Phase 6 — Advanced features (decay, multi-user, FastAPI server)
- [ ] Phase 7 — Examples & documentation
- [ ] Phase 8 — Testing, polish & launch (v1.0.0)

---

## Contributing

We welcome contributions of all kinds. Please read [CONTRIBUTING.md](CONTRIBUTING.md)
before opening a PR.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Project started: Ravi Kashyap 2025-03-22*
*Phase 1, Chapter 1.1 — Repo & Git setup*
