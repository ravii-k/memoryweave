# MemoryWeave TypeScript SDK

Universal long-term memory for any LLM application — TypeScript/JavaScript client.

## Installation

```bash
npm install @memoryweave/sdk
```

## Quick start

```typescript
import { MemoryWeave } from "@memoryweave/sdk";

const memory = new MemoryWeave({
  baseUrl: "http://localhost:8000",  // your MemoryWeave server
  sessionId: "user-123",
});

// add a memory
await memory.add("My name is Ravi and I prefer Python.");

// retrieve relevant context
const ctx = await memory.get("What language does the user prefer?");

// inject into your LLM system prompt
console.log(ctx.summary);
// → Relevant memories:
// → - My name is Ravi and I prefer Python. (relevance: 0.92)
```

## API

### `new MemoryWeave(config?)`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `baseUrl` | `string` | `http://localhost:8000` | MemoryWeave server URL |
| `sessionId` | `string` | `"default"` | Session for memory isolation |
| `topK` | `number` | `5` | Max memories to retrieve |
| `timeout` | `number` | `30000` | Request timeout (ms) |
| `apiKey` | `string` | — | API key for auth |

### Methods

- `add(text, metadata?)` → `Promise<MemoryItem>`
- `get(query, topK?)` → `Promise<MemoryContext>`
- `forget(sessionId?)` → `Promise<void>`
- `stats(sessionId?)` → `Promise<MemoryStats>`
- `isHealthy()` → `Promise<boolean>`

## Requirements

- Node.js 18+ (uses native fetch)
- A running MemoryWeave Python server

## Author

Ravi Kashyap — [github.com/ravii-k](https://github.com/ravii-k)
