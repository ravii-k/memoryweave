# Quickstart guide

Get MemoryWeave running in under 5 minutes.

---

## 1. Install

```bash
pip install memoryweave
python -m spacy download en_core_web_sm
```

## 2. Add memory and retrieve context

```python
from memoryweave import MemoryWeave

memory = MemoryWeave()

# store anything — conversations, user preferences, facts
memory.add("My name is Ravi. I work as a Python developer in India.")
memory.add("I prefer FastAPI for APIs and PostgreSQL for databases.")
memory.add("I am building an open-source memory SDK called MemoryWeave.")

# retrieve relevant context for any query
ctx = memory.get("What does this person build?")

# inject into your LLM
print(ctx.summary)
```

## 3. Plug into OpenAI

```python
from openai import OpenAI
from memoryweave import MemoryWeave

memory = MemoryWeave()
client = OpenAI()

def chat(user_message: str) -> str:
    # store the user message as a memory
    memory.add(user_message)

    # retrieve relevant past context
    ctx = memory.get(user_message)

    # inject memory into system prompt
    system = "You are a helpful assistant."
    if ctx.has_results:
        system += f"\n\nWhat you remember about this user:\n{ctx.summary}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content

# the model now remembers context across turns
print(chat("Hi, I'm Ravi and I prefer Python."))
print(chat("What language did I say I prefer?"))
# → "You mentioned that you prefer Python."
```

## 4. Multi-user sessions

```python
from memoryweave import MemoryWeave, MemoryConfig

def get_memory(user_id: str) -> MemoryWeave:
    return MemoryWeave(MemoryConfig(default_session_id=user_id))

# each user gets isolated memory
ravi_memory = get_memory("ravi-001")
alex_memory = get_memory("alex-002")

ravi_memory.add("I prefer Python.")
alex_memory.add("I prefer TypeScript.")

# no cross-session leakage
print(ravi_memory.get("language preference").summary)  # → Python
print(alex_memory.get("language preference").summary)  # → TypeScript
```

## 5. Persistent storage with ChromaDB

```python
from memoryweave import MemoryWeave, MemoryConfig

# memories survive restarts
memory = MemoryWeave(MemoryConfig(
    store_type="chroma",
    store_path="./my_memory_db",
    default_session_id="user-ravi",
))

memory.add("Ravi prefers dark mode.")
# data is now written to ./my_memory_db
# restart your app and the memory is still there
```

## 6. REST API + TypeScript

Start the Python server:
```bash
pip install fastapi uvicorn
uvicorn memoryweave.server:app --reload
```

Call from TypeScript:
```typescript
import { MemoryWeave } from "@memoryweave/sdk";

const memory = new MemoryWeave({ sessionId: "user-123" });
await memory.add("Ravi prefers Python.");
const ctx = await memory.get("language preference");
console.log(ctx.summary);
```

---

## What's available in `ctx`

```python
ctx = memory.get("query")

ctx.summary      # ready-to-inject string for LLM system prompt
ctx.entries      # list of (MemoryItem, score) from vector search
ctx.facts        # list of (fact_text, score) from knowledge graph
ctx.scores       # list of final fusion scores
ctx.has_results  # True if there is any context to inject
```

---

*More examples in the [examples/](../examples/) directory.*
